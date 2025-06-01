import sqlite3, os,sys,getopt,typing


allow_characters = ["_"]
[allow_characters.extend([chr(ord("A") + i), chr(ord("a") + i)]) for i in range(26)]
[allow_characters.append(str(i)) for i in range(10)]
sqlite_type2drift_type = {
    "INTEGER": ("IntColumn", "integer"),
    "TEXT": ("TextColumn", "text"),
    "BLOB": ("BlobColumn", "blob"),
    "REAL": ("RealColumn", "real"),
    "NUMERIC": ("RealColumn", "real"),
}


def safeUpperCamelCaseName(raw_name: str) -> str:
    formated_name = "".join(
        [word.capitalize() for word in raw_name.replace("_", " ").split(" ")]
    )
    if formated_name[0].isdigit():
        formated_name = f"_{formated_name}"
    return formated_name


def safeCamelName(raw_name: str) -> str:
    words = [word.capitalize() for word in raw_name.replace("_", " ").split(" ")]
    words[0] = words[0].lower()
    formated_name = "".join(words)
    if formated_name[0].isdigit():
        formated_name = f"_{formated_name}"
    return formated_name


def generateDartFile(db_name: str,out_file:typing.Union[str,None]) -> None:
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    cursor.execute("select name,sql from sqlite_master where type='table'")
    rows = cursor.fetchall()
    tables = {}
    for row in rows:
        name, sql = row
        sql = sql.replace(", ",", \n\r")
        if name == "sqlite_sequence":
            continue
        formated_table_name = safeUpperCamelCaseName(name)
        for character in formated_table_name:
            if character not in allow_characters:
                raise Exception(f"Table name is not allow to contain '{character}'.")
        tables[formated_table_name] = {
            "union_primary_keys": [],
            "fields": [],
            "autoincrement": None,
        }
        sql_name = '""'.join(name.split('"'))
        fields = cursor.execute(f'pragma table_info("{sql_name}")')
        for info in fields:
            tables[formated_table_name]["fields"].append(
                {
                    "name": safeCamelName(info[1]),
                    "type": info[2],
                    "not_null": info[3],
                    "default": info[4],
                    "primary_key": info[5],
                    "unique": 0,
                }
            )
        fields = sql.split("\n")[1:-1]
        if "AUTOINCREMENT)" in fields[-1]:  # autoincrement
            field = fields[-1][14:-16]
            tables[formated_table_name]["autoincrement"] = safeCamelName(field)

        elif fields[-1][1:12] == "PRIMARY KEY":  # union primary key
            union_primary_keys = field = (
                fields[-1].replace("\r", "")[14:-2].split('","')
            )
            tables[formated_table_name]["union_primary_keys"] = [
                safeCamelName(key) for key in union_primary_keys
            ]

        for field in fields:
            info = field.replace(",", "").split(" ")
            if info[-1] == "UNIQUE":
                tables[formated_table_name]["fields"][-1]["unique"] = 1
    db.close()

    basename = os.path.basename(db_name)
    filename = ".".join(basename.split(".")[:-1])
    with open((f"{filename}.dart" if not out_file else out_file), "w") as f:
        temple = "import 'package:drift/drift.dart';\nimport 'package:drift_flutter/drift_flutter.dart';\nimport 'package:path_provider/path_provider.dart';\n\npart '{}.g.dart';\n"
        f.write(temple.format((filename if not out_file else out_file[:-5])))
        for table_name in tables:
            table = tables[table_name]
            f.write(f"class {table_name} extends Table " + "{\n")
            for field in table["fields"]:
                drift_types = sqlite_type2drift_type[field["type"]]
                f.write(
                    f'  {drift_types[0]} get {safeCamelName(field["name"])} => {drift_types[1]}()'
                )
                if not field["not_null"]:
                    f.write(".nullable()")
                if field["default"]:
                    if field["type"] == "INTEGER":
                        f.write(f'.withDefault(const Constant({field["default"]}))')
                    elif field["type"] == "TEXT":
                        f.write(f'.withDefault(const Constant("{field["default"]}"))')
                    elif field["type"] == "BLOB":
                        bytes_list = bytes.fromhex(field["default"][2:-1])
                        f.write(".withDefault(Constant(Uint8List.fromList([")
                        for index in range(len(bytes_list)):
                            byte = bytes_list[index]
                            f.write(str(byte))
                            if index < len(bytes_list) - 1:
                                f.write(",")
                        f.write("])))")
                    else:  # REAL / NUMERIC
                        f.write(
                            f'.withDefault(Constant({field["default"] if "." in field["default"] else field["default"]+".0"}))'
                        )
                if field["name"] == table["autoincrement"]:
                    f.write(".autoIncrement()")
                f.write("();\n")

            if len(table["union_primary_keys"]) > 0:
                f.write("\n")
                f.write("  @override\n  Set<Column> get primaryKey => {")
                for i in range(len(table["union_primary_keys"])):
                    key = table["union_primary_keys"][i]
                    f.write(key)
                    if i < len(table["union_primary_keys"]) - 1:
                        f.write(",")
                f.write("};\n")

            f.write("}\n\n")

        f.write("@DriftDatabase(tables: [")
        for table_name in tables:
            f.write(table_name)
            f.write(",")
        f.write("])\n")
        f.write(
            f"class {safeUpperCamelCaseName(filename)} extends _$PublicOurchatDatabase "
            + "{"
        )
        f.write(
            f"  {safeUpperCamelCaseName(filename)}([QueryExecutor? executor]) : super(executor ?? _openConnection()); \n"
        )
        f.write(
            "  @override int get schemaVersion => 1;\n  static QueryExecutor _openConnection() {\n    return driftDatabase(\n      name: '"
            + safeCamelName(filename)
            + "',\n      native: const DriftNativeOptions(\n        databaseDirectory: getApplicationSupportDirectory,\n      ),\n    );\n  }\n}"
        )

    if not out_file:
        os.system(f"dart format {filename}.dart")
    else:
        os.system(f"dart format {out_file}")

if __name__ == "__main__":
    try:
        opts,_ = getopt.getopt(sys.argv[1:],"hi:o:")
    except getopt.GetoptError:
        print("usage: sqlite2drift.py -i <inputfile> -o [outputfile]")
        exit(1)
    in_file = None
    out_file = None
    for opt,arg in opts:
        if opt == "-i":
            in_file = arg
        elif opt == "-o":
            out_file = arg
    if not in_file:
        print("usage: sqlite2drift.py -i <inputfile> -o [outputfile]")
        exit(1)
    generateDartFile(in_file,out_file)
# schemagen_tsi.py

'''Generate SQL that will create a suitable schema for storing data from ATOC
.ZTR timetable files. This is done dynamically to ensure it keeps in sync with
the definitions in nrcif.py, tsi_reader.py and nrcif_fields.py'''

import tsi_reader

import argparse, contextlib

SCHEMA = "tsi"

parser = argparse.ArgumentParser()
parser.add_argument("DDL", help = "The destination for the SQL DDL file (default schema_tsi_ddl.gen.sql)",
                            nargs = "?", default = "schema_tsi_ddl.gen.sql", type=argparse.FileType("w"))

args = parser.parse_args()

with contextlib.closing(args.DDL) as DDL:

    DDL.write('''-- SQL DDL for data extracted from ATOC .TSI interchange files in
-- CSV format. Auto-generated by schemagen_tsi.py\n\n''')


    DDL.write("CREATE SCHEMA {0};\nSET search_path TO {0},public;\n\n".format(SCHEMA))

    DDL.write('''-- Only one table\n''')
    DDL.write("CREATE TABLE tsi (\n")

    first_field = False
    for i in tsi_reader.TSI.layout:
        if not first_field:
            first_field=True
        else:
            DDL.write(",\n")
        fieldname = i.name.lower().replace(" ","_")
        DDL.write("\t{0}\t\t{1}".format(fieldname, i.sql_type))

    DDL.write("\n\t);\n\n")

    DDL.write('''SET search_path TO "$user",public;\n''')


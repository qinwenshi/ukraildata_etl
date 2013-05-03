# schemagen_msn.py

'''Generate SQL that will create a suitable schema for storing data from ATOC
.MSN timetable files. This is done dynamically to ensure it keeps in sync with
the definitions in nrcif.py and nrcif_fields.py'''

from nrcif.msn_records import layouts

import argparse, contextlib

SCHEMA = "msn"

parser = argparse.ArgumentParser()
parser.add_argument("DDL", help = "The destination for the SQL DDL file (default schema_msn_ddl.gen.sql)",
                            nargs = "?", default = "schema_msn_ddl.gen.sql", type=argparse.FileType("w"))
parser.add_argument("CONS", help = "The destination for the SQL constraints & indexes file (default schema_msn_cons.gen.sql)",
                            nargs = "?", default = "schema_msn_cons.gen.sql", type=argparse.FileType("w"))

args = parser.parse_args()

with contextlib.closing(args.DDL) as DDL, contextlib.closing(args.CONS) as CONS:

    DDL.write('''-- SQL DDL for data extracted from ATOC .MSN timetable files in
-- NR CIF format. Auto-generated by schemagen_msn.py\n\n''')

    CONS.write('''-- SQL constraints & indexes definitions for data extracted from ATOC .MSN timetable files in
-- NR CIF format. Auto-generated by schemagen_msn.py\n\n''')

    DDL.write("CREATE SCHEMA {0};\nSET search_path TO {0},public;\n\n".format(SCHEMA))
    CONS.write("SET search_path TO {0},public;\n\n".format(SCHEMA))

    normal_template = "CREATE TABLE {} (\n"

    for i in ('A', 'L', 'V'):
        tablename = layouts[i].name.lower().replace(" ", "_")
        DDL.write(normal_template.format(tablename))
        DDL.write(layouts[i].generate_sql_ddl())
        DDL.write("\n\t);\n\n")

    CONS.write("ALTER TABLE station_detail ADD PRIMARY KEY(tiploc_code);\n")
    CONS.write("CREATE INDEX idx_stn_detail_stn_name ON station_detail (station_name);\n")
    CONS.write("CREATE INDEX idx_stn_detail_3alpha ON station_detail (_3_alpha_code);\n")
    CONS.write("CREATE INDEX idx_stn_alias_stn_name ON station_alias (station_name);\n")
    CONS.write("CREATE INDEX idx_stn_alias_alias_name ON station_alias (alias_name);\n")
    CONS.write("ALTER TABLE routeing_groups ADD PRIMARY KEY(group_name);\n")
    CONS.write("\n")

    DDL.write('''SET search_path TO "$user",public;\n''')
    CONS.write('''SET search_path TO "$user",public;\n''')

# schemagen_ztr.py

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

'''Generate SQL that will create a suitable schema for storing data from ATOC
.ZTR timetable files. This is done dynamically to ensure it keeps in sync with
the definitions in nrcif.py, ztr_reader.py and nrcif_fields.py'''

from ..records import layouts as mca_layouts

from ..ztr_reader import reduced_hd, corrected_bx

def gen_sql(DDL, CONS):

    SCHEMA = "ztr"

    layouts = mca_layouts.copy()
    layouts["HD"] = reduced_hd
    layouts["BX"] = corrected_bx

    DDL.write('''-- SQL DDL for data extracted from ATOC .ZTR timetable files in
-- NR CIF format. Auto-generated by schemagen_ztr.py\n\n''')

    CONS.write('''-- SQL constraints & indexes definitions for data extracted from ATOC .ZTR timetable files in
-- NR CIF format. Auto-generated by schemagen_ztr.py\n\n''')

    DDL.write("CREATE SCHEMA {0};\nSET search_path TO {0},public;\n\n".format(SCHEMA))
    CONS.write("SET search_path TO {0},public;\n\n".format(SCHEMA))

    DDL.write('''-- The BS, BX and TN records are stored in the same table\n''')
    DDL.write("CREATE TABLE basic_schedule (\n")

    DDL.write(layouts['BS'].generate_sql_ddl()+",\n")
    DDL.write(layouts['BX'].generate_sql_ddl()+",\n")
    DDL.write(layouts['TN'].generate_sql_ddl())

    DDL.write("\n\t);\n\n")

    CONS.write("-- ***The Z-Trains data appears to contain duplicates, so primary keys cannot be used***\n\n")
    CONS.write("CREATE INDEX idx_ztr_basic_schedule ON basic_schedule (train_uid, date_runs_from, stp_indicator);\n")

    DDL.write('''-- The LO, LI, CR, LT and LN tables all have a header added to relate
-- them to the relevant train\n''')

    route_template = '''CREATE TABLE {} (
\ttrain_uid\t\tCHAR(6),
\tdate_runs_from\tDATE,
\tstp_indicator\tCHAR(1),
\tloc_order\t\tINTEGER,
\txmidnight\t\tBOOLEAN,
'''
    route_pk = '''CREATE INDEX idx_ztr_{0} ON ztr.{0} (train_uid, date_runs_from, stp_indicator, loc_order);
--ALTER TABLE {0} ADD FOREIGN KEY (train_uid, date_runs_from, stp_indicator)
--    REFERENCES basic_schedule (train_uid, date_runs_from, stp_indicator) DEFERRABLE;

'''

    for i in ('LO', 'LI', 'CR', 'LT', 'LN'):
        tablename = layouts[i].name.lower().replace(" ", "_")
        DDL.write(route_template.format(tablename))
        DDL.write(layouts[i].generate_sql_ddl())
        DDL.write("\n\t);\n\n")
        CONS.write(route_pk.format(tablename))

    normal_template = "CREATE TABLE {} (\n"
    tiploc_pk = "ALTER TABLE {} ADD PRIMARY KEY (tiploc_code);\n\n"

    for i in ('AA', 'TI', 'TA', 'TD'):
        tablename = layouts[i].name.lower().replace(" ", "_")
        DDL.write(normal_template.format(tablename))
        DDL.write(layouts[i].generate_sql_ddl())
        DDL.write("\n\t);\n\n")
        if i != 'AA':
            CONS.write(tiploc_pk.format(tablename))

    DDL.write('''SET search_path TO "$user",public;\n\n''')
    CONS.write('''SET search_path TO "$user",public;\n\n''')

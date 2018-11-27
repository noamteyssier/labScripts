#!/usr/bin/env python3

import sqlite3
import os
import sys
import argparse

def sql_string(val):
    return ''.join(["'", str(val), "'"])
def get_study_index(cursor, study_name):
    """return index of study"""
    try:
        study_ix = cursor.execute(
            'SELECT * from study where title = (?)', (study_name,)
        ).fetchone()[0]
    except TypeError:
        sys.exit('ERROR : study name missing from database')

    return study_ix
def add_matrix_plate(source, destination, plate_name):
    """create matrix plate in destination"""

    # pull tuple from source db
    c = source.execute(
        "SELECT * from matrix_plate where uid = (?)", (plate_name,)
    ).fetchone()

    # values of database
    colnames = ('created', 'last_updated', 'uid', 'hidden', 'location_id')

    # values of destination (defaults of hidden/location_id)
    values = c[1:-2]+(0, 1)

    # import source matrix_plate to destination
    destination.execute(
        "INSERT INTO matrix_plate {0} VALUES {1}".format(colnames, values)
    )
def add_matrix_tubes(source, destination, plate_name):
    """insert matrix tubes from source plate to destination database"""

    # identity source plate id
    source_plate_id = source.execute(
        "SELECT * from matrix_plate where uid = (?)", (plate_name,)
    ).fetchone()[0]

    # identify destination plate id
    destination_plate_id = destination.execute(
        "SELECT * from matrix_plate where uid = (?)", (plate_name,)
    ).fetchone()[0]

    # get all tubes that belong to source plate
    tubes = source.execute(
        "SELECT * from matrix_tube where plate_id = (?)", (source_plate_id, )
    ).fetchall()

    # lists of tube ids from source to destination
    source_tube_ids = []
    destination_tube_ids = []

    # append tubes to destination db
    colnames = ('plate_id', 'barcode', 'well_position')
    for t in tubes:
        t_values = (destination_plate_id,)+t[2:]
        destination.execute(
            "INSERT INTO matrix_tube {0} VALUES {1}".format(colnames, t_values)
        )


        # keep track of source and destination tube ids for specimen linking
        source_tube_ids.append(t[0])
        destination_tube_ids.append(destination.execute(
            "SELECT * from matrix_tube where barcode = {0}".format(t[2])
        ).fetchone()[0])

    return source_tube_ids, destination_tube_ids
def transfer_study_subjects(source, destination, sti, dti):

    numTubes = len(sti)
    colnames_ss = ('created', 'last_updated', 'uid', 'study_id')
    colnames_specimen = ('created', 'last_updated', 'study_subject_id', 'specimen_type_id', 'collection_date')
    colnames_storage = ('id', 'created', 'last_updated', 'type', 'specimen_id', 'comments', 'exhausted')

    for i in range(numTubes):

        # pull specimen id from storage container with tube id
        source_storage_container = source.execute(
            "SELECT * FROM storage_container WHERE id = {0}".format(sti[i])
        ).fetchone()

        # pull study subject id from specimen
        source_specimen = source.execute(
            "SELECT * FROM specimen WHERE id = {0}".format(source_storage_container[4]) # specimen_id
        ).fetchone()

        # pull study subject from study subject id
        source_study_subject = source.execute(
            "SELECT * FROM study_subject WHERE id = {0}".format(source_specimen[3]) # study_subject_id
        ).fetchone()

        # get study index in destination
        source_study_name = source.execute(
            "SELECT * FROM study WHERE id = {0}".format(source_study_subject[4]) # study_id
        ).fetchone()[3]
        d_study_ix = get_study_index(destination, source_study_name)

        # transfer subject id from source to destination if not already there
        try:
            destination.execute(
                "INSERT INTO study_subject {0} VALUES {1}".format(colnames_ss, source_study_subject[1:-1] + (d_study_ix, ))
            )
        except sqlite3.IntegrityError:
            # study subject exists already
            pass


        # destination study subject id
        study_uid = sql_string(source_study_subject[3])
        d_ss_ix = destination.execute(
            "SELECT * FROM study_subject WHERE uid = {0}".format(study_uid) # study_subject_uid
        ).fetchone()[0]


        # merge source_created/updated + destination subject id + collection date
        try:
            specimen_vals = source_specimen[1:3] + (d_ss_ix, 1) + (source_specimen[-1],)

            destination.execute(
                "INSERT INTO specimen {0} VALUES {1}".format(colnames_specimen, specimen_vals)
            )

            date = sql_string(source_specimen[-1])
            destination_specimen = destination.execute(
                "SELECT * FROM specimen WHERE study_subject_id = {0} AND collection_date = {1}".format(specimen_vals[2], date)
            ).fetchone()

        except sqlite3.OperationalError:
            specimen_vals = source_specimen[1:3] + (d_ss_ix, 1)
            destination.execute(
                "INSERT INTO specimen {0} VALUES {1}".format(colnames_specimen[:-1], specimen_vals)
            )

            destination_specimen = destination.execute(
                "SELECT * FROM specimen WHERE study_subject_id = {0}".format(specimen_vals[2])
            ).fetchone()


        storage_vals = (dti[i], )+ source_storage_container[1:4] + (destination_specimen[0],) + source_storage_container[-2:]

        destination.execute(
            "INSERT INTO storage_container {0} VALUES {1}".format(colnames_storage, storage_vals)
        )






def main():

    p = argparse.ArgumentParser()
    p.add_argument('-1', '--source', help='source sqlite to transfer plate from', required=True)
    p.add_argument('-2', '--destination', help='destination sqlite to transfer plate to', required=True)
    p.add_argument('-i', '--plate_name', help='plate name to transfer from source to destination', required=True)
    args = p.parse_args()

    source_sqlite = sqlite3.connect(args.source)
    destination_sqlite = sqlite3.connect(args.destination)
    plate_name = args.plate_name

    source = source_sqlite.cursor()
    destination = destination_sqlite.cursor()

    add_matrix_plate(source, destination, plate_name)
    sti, dti = add_matrix_tubes(source, destination, plate_name)
    transfer_study_subjects(source, destination, sti, dti)


    destination_sqlite.commit()
    destination_sqlite.close()



if __name__ == '__main__':
    main()

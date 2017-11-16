#!/usr/bin/env bats
# -----------------------------------------------------------------------------
# (C) British Crown Copyright 2017 Met Office.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

@test "spotdb -h" {
  run improver spotdb -h
  [[ "$status" -eq 0 ]]
  read -d '' expected <<'__HELP__' || true
usage: improver-spotdb [-h] [--table_name OUTPUT_TABLE_NAME]
                       [--experiment_id EXPERIMENT_ID] (--sqlite | --csv)
                       [-rows ROW_DIMENSION] [-cols EXTRA_COLUMNS]
                       [-col_vals EXTRA_VALUES]
                       INPUT_FILES OUTPUT_FILE

Convert spot forecast cubes to a table and save in csv or as a sql database.
For all the spot files provided it creates a table in memory and then saves it
in the form specified by the user.

positional arguments:
  INPUT_FILES           A path (with wildcards if necessary) to input NetCDF
                        files to be processed.
  OUTPUT_FILE           The output path for the processed database.

optional arguments:
  -h, --help            show this help message and exit
  --table_name OUTPUT_TABLE_NAME
                        The name of the table for the processed database.
  --experiment_id EXPERIMENT_ID
                        A name to provide as the experiment identifier, which
                        refers to the post-processing stage the input data
                        comes from
  --sqlite              Create or append to a SQLite Database file.
  --csv                 The option used to create a CSV file.

Table format options:
  Options for structure of the output table.

  -rows ROW_DIMENSION, --row_dimension ROW_DIMENSION
                        A dimension to turn into the table rows
  -cols EXTRA_COLUMNS, --extra_columns EXTRA_COLUMNS
                        Any extra columns to append to the table
  -col_vals EXTRA_VALUES, --extra_values EXTRA_VALUES
                        Values for any extra columns to append
__HELP__
  [[ "$output" == "$expected" ]]
}

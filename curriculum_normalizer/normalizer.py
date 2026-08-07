import re
from datetime import datetime

import pandas as pd

from config import (
    INPUT_WORKBOOK,
    MASTER_LESSON_DB,
    CURRICULUM_VERSION,
    VERSION
)


# ==========================================================
# Curriculum Normalizer
# ==========================================================

class CurriculumNormalizer:

    def __init__(self):

        self.df = pd.read_excel(

            INPUT_WORKBOOK,

            sheet_name="Learning areas"

        )

        self.original_df = None

        self.parent_lookup = {}

        self.validation_errors = []

    # ==========================================================
    # Prepare
    # ==========================================================

    def prepare(self):

        #
        # Standardise headings
        #

        self.df.columns = [

            str(c).strip()

            for c in self.df.columns

        ]

        #
        # Rename duplicate Level columns
        #

        cols = list(self.df.columns)

        level_count = 0

        for i, col in enumerate(cols):

            if col == "Level":

                level_count += 1

                if level_count == 1:

                    cols[i] = "Year Level"

                else:

                    cols[i] = "Level Description"

        self.df.columns = cols
        #
        # Replace NaN only
        #

        self.df.fillna(

            "",

            inplace=True

        )
        self.df.replace("nan", "", inplace=True)

        self.df.replace("NaN", "", inplace=True)

        #
        # Preserve original workbook
        #

        self.original_df = self.df.copy()

        return self

    # ==========================================================
    # Build Parent Lookup
    # ==========================================================

    def build_parent_lookup(self):

        """
        Every curriculum parent row (AC9xxxxx)
        becomes the master source for all
        elaboration rows (AC9xxxxx_E1...)

        No forward-fill is used.
        """

        self.parent_lookup = {}

        current = {

            "Learning Area": "",

            "Subject": "",

            "Year Level": "",

            "School Level": "",

            "Pathway": "",

            "Sequence": "",

            "Strand": "",

            "Sub-Strand": ""

        }

        for _, row in self.original_df.iterrows():

            #
            # Learning Area
            #

            value = str(row["Learning Area"]).strip()

            if value and value.lower() != "nan":
                current["Learning Area"] = value

            #
            # Subject
            #

            value = str(row["Subject"]).strip()

            if value and value.lower() != "nan":
                current["Subject"] = value

            #
            # Year Level
            #

            value = str(row["Year Level"]).strip()
            if value and value.lower() != "nan":
                current["Year Level"] = value

            #
            # Pathway
            #

            value = str(row["Pathway"]).strip()

            if value and value.lower() != "nan":
                current["Pathway"] = value

            #
            # Sequence
            #

            value = str(row["Sequence"]).strip()

            if value and value.lower() != "nan":
                current["Sequence"] = value

            #
            # Strand
            #

            value = str(row["Strand"]).strip()

            if value and value.lower() != "nan":
                current["Strand"] = value

                #
                # New Strand starts.
                # Reset Sub-Strand.
                #

                current["Sub-Strand"] = ""

            #
            # Sub-Strand
            #

            value = str(row["Sub-Strand"]).strip()

            if value and value.lower() != "nan":
                current["Sub-Strand"] = value

            #
            # IMPORTANT
            #
            # Blank Sub-Strands remain blank.
            #
            # They NEVER inherit from another topic.
            #
            if row["Sub-Strand"] != "":
                current["Sub-Strand"] = row["Sub-Strand"]

            code = str(

                row["Code"]

            ).strip()

            #
            # Parent curriculum rows only
            #

            if (

                    code.startswith("AC9")

                    and

                    "_E" not in code

            ):
                print(
                    code,
                    current["Learning Area"],
                    current["Subject"],
                    current["Year Level"],
                    current["Strand"],
                    current["Sub-Strand"]
                )

                self.parent_lookup[code] = {

                    "Learning Area":

                        current["Learning Area"],

                    "Subject":

                        current["Subject"],

                    "Year Level":

                        current["Year Level"],

                    "School Level":

                        current["School Level"],

                    "Pathway":

                        current["Pathway"],

                    "Sequence":

                        current["Sequence"],

                    "Strand":

                        current["Strand"],

                    "Sub-Strand":

                        current["Sub-Strand"],

                    "Content Description":

                        row["Content Description"]

                }
        print("=" * 70)

        return self

    # ==========================================================
    # Keep Elaborations Only
    # ==========================================================

    def keep_elaborations(self):

        self.df = self.df[

            self.df["Code"]

            .astype(str)

            .str.contains(

                r"_E\d+$"
            )

        ].copy()

        self.df.reset_index(

            drop=True,

            inplace=True

        )
        print("=" * 60)
        print("After keep_elaborations")
        print("Rows:", len(self.df))
        print(self.df["Code"].head())
        print("=" * 60)

        return self

    # ==========================================================
    # Apply Parent Lookup
    # ==========================================================

    def apply_parent_lookup(self):

        learning_area = []
        subject = []
        year_level = []
        school_level = []
        pathway = []
        sequence = []
        strand = []
        sub_strand = []
        content_description = []
        parent_codes = []

        for _, row in self.df.iterrows():
            curriculum_code = str(

                row["Code"]

            ).strip()

            parent_code = curriculum_code.replace(

                "_E1", ""

            ).replace(

                "_E2", ""

            ).replace(

                "_E3", ""

            ).replace(

                "_E4", ""

            ).replace(

                "_E5", ""

            ).replace(

                "_E6", ""

            ).replace(

                "_E7", ""

            ).replace(

                "_E8", ""

            )

            parent = self.parent_lookup.get(

                parent_code,

                {}

            )

            learning_area.append(

                parent.get(

                    "Learning Area",

                    ""

                )

            )

            subject.append(

                parent.get(

                    "Subject",

                    ""

                )

            )

            year_level.append(

                parent.get(

                    "Year Level",

                    ""

                )

            )

            pathway.append(

                parent.get(

                    "Pathway",

                    ""

                )

            )

            sequence.append(

                parent.get(

                    "Sequence",

                    ""

                )

            )

            strand.append(

                parent.get(

                    "Strand",

                    ""

                )

            )

            #
            # IMPORTANT
            #
            # Blank stays blank.
            #

            sub_strand.append(

                parent.get(

                    "Sub-Strand",

                    ""

                )

            )

            content_description.append(

                parent.get(

                    "Content Description",

                    ""

                )

            )

            parent_codes.append(

                parent_code

            )

        self.df["Learning Area"] = learning_area

        self.df["Subject"] = subject

        self.df["Year Level"] = year_level

        self.df["Pathway"] = pathway

        self.df["Sequence"] = sequence

        self.df["Strand"] = strand

        self.df["Sub-Strand"] = sub_strand

        self.df["Content Description"] = content_description

        self.df["Parent Code"] = parent_codes

        return self

    # ==========================================================
    # Topic Lesson Numbers
    # ==========================================================

    def topic_lesson_numbers(self):

        counters = {}

        numbers = []

        for _, row in self.df.iterrows():
            parent = row["Parent Code"]

            counters[parent] = counters.get(

                parent,

                0

            ) + 1

            numbers.append(

                counters[parent]

            )

        self.df["Topic Lesson Number"] = numbers

        return self

    # ==========================================================
    # Lesson Numbers
    # ==========================================================

    def lesson_numbers(self):

        self.df["Lesson Number"] = range(

            1,

            len(self.df) + 1

        )

        return self

    # ==========================================================
    # Topic Titles
    # ==========================================================

    def populate_topics(self):

        topics = []

        for _, row in self.df.iterrows():

            description = str(

                row["Content Description"]

            ).strip()

            if description == "":
                topics.append("")

                continue

            sentence = description.split(".")[0]

            sentence = sentence.split(";")[0]

            sentence = sentence.rstrip(",")

            words = sentence.split()

            if len(words) > 12:
                sentence = " ".join(

                    words[:12]

                ) + "..."

            topics.append(

                sentence

            )

        self.df["Topics"] = topics

        return self

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def slug(value):

        return re.sub(

            r"[^A-Z0-9]+",

            "_",

            str(value).upper()

        ).strip("_")

    @staticmethod
    def year_short(year):

        match = re.search(

            r"(\d+)",

            str(year)

        )

        if match:
            return f"Y{match.group(1)}"

        if "Foundation" in str(year):
            return "FY"

        return CurriculumNormalizer.slug(year)

    # ==========================================================
    # Topic IDs
    # ==========================================================

    def topic_ids(self):

        topic_ids = []

        lesson_packages = []

        for _, row in self.df.iterrows():
            subject = self.slug(

                row["Subject"]

            )[:3]

            year = self.year_short(

                row["Year Level"]

            )

            curriculum = self.slug(

                row["Code"]

            )

            lesson = int(

                row["Topic Lesson Number"]

            )

            topic_id = "_".join([

                subject,

                year,

                curriculum,

                f"L{lesson:02d}"

            ])

            topic_ids.append(

                topic_id

            )

            lesson_packages.append(

                "LP_" + topic_id

            )

        self.df["Topic ID"] = topic_ids

        self.df["Lesson Package ID"] = lesson_packages

        return self

    #
    # NOTE
    #
    # Version 1.0
    #
    # Master_Lesson_DB is rebuilt from scratch
    # every time /normalize is executed.
    #
    # Therefore:
    #
    # Created = normalization timestamp
    # Updated = normalization timestamp
    #
    # In a future version, Created will be
    # preserved across normalizations while
    # Updated will reflect the latest rebuild.
    #
    # ==========================================================
    # Production Metadata
    # ==========================================================

    def production_defaults(self):

        now = datetime.now().strftime(

            "%Y-%m-%d %H:%M:%S"

        )

        #
        # Curriculum metadata
        #

        self.df["Curriculum Version"] = CURRICULUM_VERSION

        self.df["Version"] = VERSION

        #
        # Master Lesson Database timestamps
        #
        # Since /normalize rebuilds the entire
        # Master_Lesson_DB, every row is both
        # created and updated at this time.
        #

        self.df["Created"] = now

        self.df["Updated"] = now

        return self


def rename_columns(self):
    #
    # Remove original Level column if Year Level already exists
    #

    self.df.rename(
        columns={
            "Code": "Curriculum Code"
        },
        inplace=True
    )

    return self


# ==========================================================
# Reorder Columns
# ==========================================================

def reorder_columns(self):
    columns = [

        "Learning Area",

        "Subject",

        "Year Level",

        "School Level",

        "Strand",

        "Sub-Strand",

        "Parent Code",

        "Curriculum Code",

        "Content Description",

        "Topics",

        "Elaboration",

        "Topic Lesson Number",

        "Topic ID",

        "Lesson Package ID",

        "Lesson Number",

        "Curriculum Version",

        "Version",

        "Created",

        "Updated"

    ]

    self.df = self.df[columns]

    return self


# ==========================================================
# Validation
# ==========================================================

def validate(self):
    errors = []

    #
    # Duplicate Topic IDs
    #

    duplicates = self.df[

        self.df["Topic ID"].duplicated()

    ]

    if len(duplicates):
        errors.append(

            f"Duplicate Topic IDs: {len(duplicates)}"

        )

    #
    # Duplicate Lesson Package IDs
    #

    duplicates = self.df[

        self.df["Lesson Package ID"].duplicated()

    ]

    if len(duplicates):
        errors.append(

            f"Duplicate Lesson Package IDs: {len(duplicates)}"

        )

    #
    # Blank Parent Codes
    #

    blanks = self.df[

        self.df["Parent Code"] == ""

        ]

    if len(blanks):
        errors.append(

            f"Blank Parent Codes: {len(blanks)}"

        )

    #
    # Blank Curriculum Codes
    #

    blanks = self.df[

        self.df["Curriculum Code"] == ""

        ]

    if len(blanks):
        errors.append(

            f"Blank Curriculum Codes: {len(blanks)}"

        )

    #
    # Blank Topic IDs
    #

    blanks = self.df[

        self.df["Topic ID"] == ""

        ]

    if len(blanks):
        errors.append(

            f"Blank Topic IDs: {len(blanks)}"

        )

    #
    # Blank Lesson Package IDs
    #

    blanks = self.df[

        self.df["Lesson Package ID"] == ""

        ]

    if len(blanks):
        errors.append(

            f"Blank Lesson Package IDs: {len(blanks)}"

        )

    #
    # Blank Topics
    #

    blanks = self.df[

        self.df["Topics"] == ""

        ]

    if len(blanks):
        errors.append(

            f"Blank Topics: {len(blanks)}"

        )

    self.validation_errors = errors

    return self


# ==========================================================
# Validation Helpers
# ==========================================================

def is_valid(self):
    return len(

        self.validation_errors

    ) == 0


def validation_summary(self):
    return {

        "valid":

            self.is_valid(),

        "errors":

            self.validation_errors,

        "rows":

            len(self.df)

    }


# ==========================================================
# Write Master Lesson DB
# ==========================================================

def write_master_database(self):
    self.df.to_excel(

        MASTER_LESSON_DB,

        sheet_name="Lesson_DB",

        index=False

    )

    return self


def school_level(self):
    school_levels = []

    for year in self.df["Year Level"]:

        year = str(year)

        if year in [

            "Foundation",

            "Foundation Year",

            "Year 1",

            "Year 2",

            "Year 3",

            "Year 4",

            "Year 5",

            "Year 6"

        ]:

            school_levels.append(

                "Primary"

            )

        else:

            school_levels.append(

                "Secondary"

            )
    self.df["School Level"] = school_levels
    return self


# ==========================================================
# Run
# ==========================================================

def run(self):
    return (

        self

        #
        # Load workbook
        #

        .prepare()

        #
        # Build parent lookup
        #

        .build_parent_lookup()

        #
        # Keep only elaboration rows
        #

        .keep_elaborations()

        #
        # Copy hierarchy from parent rows
        #

        .apply_parent_lookup()

        #
        # Derive School Level
        #

        .school_level()

        #
        # Lesson numbering
        #

        .lesson_numbers()

        .topic_lesson_numbers()

        #
        # Topic titles
        #

        .populate_topics()

        #
        # Topic IDs
        #

        .topic_ids()

        #
        # Production metadata
        #

        .production_defaults()

        #
        # Rename columns
        #

        .rename_columns()

        #
        # Final workbook layout
        #

        .reorder_columns()

        #
        # Validation
        #

        .validate()

        #
        # Save Master Lesson Database
        #

        .write_master_database()

    )

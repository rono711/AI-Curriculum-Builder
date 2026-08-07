from pathlib import Path
import pandas as pd

from config import MASTER_LESSON_DB


class MasterDB:

    # =====================================================
    # Constructor
    # =====================================================

    def __init__(self):
        self.reload()

    # =====================================================
    # Reload Workbook
    # =====================================================

    from pathlib import Path
    import pandas as pd

    def reload(self):
        if not Path(MASTER_LESSON_DB).exists():
            print()

            print("=" * 70)
            print("Master Lesson DB not found.")
            print("Waiting for /normalize ...")
            print("=" * 70)

            self.df = pd.DataFrame()

            return

        self.df = pd.read_excel(

            MASTER_LESSON_DB

        )

    # =====================================================
    # Refresh
    # =====================================================

    def refresh(self):
        self.reload()

    # =====================================================
    # Learning Areas
    # =====================================================

    def learning_areas(self):
        values = sorted(

            self.df["Learning Area"]

            .astype(str)

            .str.strip()

            .unique()

            .tolist()

        )

        return values

    # =====================================================
    # Subjects
    # =====================================================

    def subjects(self, learning_area):
        df = self.df[

            self.df["Learning Area"] == learning_area

            ]

        values = sorted(

            df["Subject"]

            .astype(str)

            .str.strip()

            .unique()

            .tolist()

        )

        return values

    # =====================================================
    # Year Levels
    # =====================================================

    def year_levels(self, learning_area, subject):
        df = self.df[

            (self.df["Learning Area"] == learning_area)

            &

            (self.df["Subject"] == subject)

            ]

        values = (

            df["Year Level"]

            .astype(str)

            .str.strip()

            .unique()

            .tolist()

        )

        return values

    # =====================================================
    # Strands
    # =====================================================

    def strands(

            self,

            learning_area,

            subject,

            year_level

    ):
        df = self.df[

            (self.df["Learning Area"] == learning_area)

            &

            (self.df["Subject"] == subject)

            &

            (self.df["Year Level"] == year_level)

            ]

        values = sorted(

            df["Strand"]

            .astype(str)

            .str.strip()

            .unique()

            .tolist()

        )

        return values

    # =====================================================
    # Sub-Strands / Curriculum Focus
    # =====================================================

    def sub_strands(

            self,

            learning_area,

            subject,

            year_level,

            strand

    ):
        df = self.df[

            (self.df["Learning Area"] == learning_area)

            &

            (self.df["Subject"] == subject)

            &

            (self.df["Year Level"] == year_level)

            &

            (self.df["Strand"] == strand)

            ].copy()

        #
        # Preserve curriculum order
        #

        df = df.sort_values(

            "Parent Code"

        )

        #
        # Real Sub-Strands exist
        #

        values = (

            df["Sub-Strand"]

            .fillna("")

            .astype(str)

            .str.strip()

            .replace(

                ["", "nan", "NaN"],

                pd.NA

            )

            .dropna()

            .unique()

            .tolist()

        )

        if len(values) > 0:
            return values

        #
        # No Sub-Strands
        # Return Content Descriptions
        #

        values = (

            df["Content Description"]

            .fillna("")

            .astype(str)

            .str.strip()

            .replace(

                ["", "nan", "NaN"],

                pd.NA

            )

            .dropna()

            .unique()

            .tolist()

        )

        return values

        # =====================================================
        # Curriculum Topics
        # =====================================================

    def topics(

            self,

            learning_area,

            subject,

            year_level,

            strand,

            sub_strand=""

    ):
        df = self.df[

            (self.df["Learning Area"] == learning_area)

            &

            (self.df["Subject"] == subject)

            &

            (self.df["Year Level"] == year_level)

            &

            (self.df["Strand"] == strand)

            ].copy()

        df = df.sort_values(

            "Parent Code"

        )

        #
        # Real Sub-Strands exist
        #

        has_sub_strands = (

                df["Sub-Strand"]

                .fillna("")

                .astype(str)

                .str.strip()

                .replace("", pd.NA)

                .dropna()

                .size > 0

        )

        if has_sub_strands:

            df = df[

                df["Sub-Strand"] == sub_strand

                ]

        else:

            df = df[

                df["Content Description"] == sub_strand

                ]

        topics = []

        for _, row in df.iterrows():
            topics.append(

                {

                    "parent_code":

                        row["Parent Code"],

                    "topic":

                        row["Elaboration"]

                }

            )

        return topics

        # =====================================================
        # Lessons
        # =====================================================

    def lessons(

            self,

            parent_code

    ):
        df = self.df[

            self.df["Parent Code"] == parent_code

            ]

        df = df.sort_values(

            "Topic Lesson Number"

        )

        lessons = []

        for _, row in df.iterrows():

            title = row["Topics"]

            if not title:
                title = row["Elaboration"]

            lessons.append(

                {

                    "lesson_number":

                        int(

                            row["Topic Lesson Number"]

                        ),

                    "topic_id":

                        row["Topic ID"],

                    "lesson_package_id":

                        row["Lesson Package ID"],

                    "lesson":

                        row["Elaboration"]

                }

            )

        return lessons

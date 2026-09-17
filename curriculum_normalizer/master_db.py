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
    # Clean Dropdown Values
    # =====================================================

    @staticmethod
    def _clean_values(series):

        return sorted(
            series
            .dropna()
            .astype(str)
            .str.strip()
            .loc[lambda s: s != ""]
            .unique()
            .tolist()
        )

    # =====================================================
    # Learning Areas
    # =====================================================

    def learning_areas(self):
        return self._clean_values(
            self.df["Learning Area"]
        )

    # =====================================================
    # Subjects
    # =====================================================

    def subjects(self, learning_area):
        df = self.df[

            self.df["Learning Area"] == learning_area

            ]

        values = self._clean_values(
            df["Subject"]
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

        values = self._clean_values(
            df["Year Level"]
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

        values = self._clean_values(
            df["Strand"]
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

    def curriculum_focuses(
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

        df = df.sort_values(
            "Parent Code"
        )

        sub_strands = (
            df["Sub-Strand"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        has_sub_strands = (
            sub_strands
            .replace(
                ["", "nan", "NaN"],
                pd.NA
            )
            .dropna()
            .shape[0]
            > 0
        )

        value_column = (
            "Sub-Strand"
            if has_sub_strands
            else "Content Description"
        )

        results = []
        seen = set()

        for _, row in df.iterrows():

            value = str(
                row.get(value_column, "") or ""
            ).strip()

            parent_code = str(
                row.get("Parent Code", "") or ""
            ).strip()

            if (
                not value
                or value in ("nan", "NaN")
                or not parent_code
                or parent_code in ("nan", "NaN")
            ):
                continue

            key = (
                parent_code,
                value
            )

            if key in seen:
                continue

            seen.add(key)

            results.append({
                "parent_code": parent_code,
                "focus": value,
                "display":
                    parent_code
                    + " — "
                    + value
            })

        return results


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

    # =====================================================
    # Canonical Curriculum Order
    # =====================================================

    def canonical_order(
            self,
            curriculum_codes=None
    ):
        """
        Return curriculum lessons in their original
        Master_Lesson_DB workbook row order.

        No alphabetical, click-order, or publication-order
        sorting is applied.
        """

        df = self.df.copy()

        if curriculum_codes:
            wanted = {
                str(value).strip()
                for value in curriculum_codes
                if str(value).strip()
            }

            df = df[
                df["Curriculum Code"]
                .astype(str)
                .str.strip()
                .isin(wanted)
            ]

        results = []

        for source_position, (_, row) in enumerate(
            df.iterrows(),
            start=1
        ):
            results.append({
                "source_position":
                    int(source_position),

                "curriculum_code":
                    str(
                        row["Curriculum Code"]
                    ).strip(),

                "parent_code":
                    str(
                        row["Parent Code"]
                    ).strip(),

                "lesson_number":
                    int(
                        row["Topic Lesson Number"]
                    ),
            })

        return results


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

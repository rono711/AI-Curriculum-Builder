# Rono Publisher

## Moodle Local Plugin

**Component:** `local_rono_publisher`

**Plugin Type:** Local Plugin

**Development Stage:** Moodle 5.2 structural publishing test, followed
by Question Bank and Quiz integration.

**Author:** Mohammad Hassan

------------------------------------------------------------------------

# Purpose

Rono Publisher is the Moodle publishing layer for the Rono's School AI
Curriculum Platform.

The plugin receives a complete lesson/elaboration publishing request
from the Publisher Engine and publishes the corresponding curriculum
structure and learning activities into Moodle.

The plugin does **not** generate AI content. AI-generated lesson
content, Gamma material, quiz questions, activities, and recap content
are prepared upstream by the Curriculum Builder platform and Publisher
Engine.

------------------------------------------------------------------------

# Platform Architecture

``` text
Teacher
   |
   v
Build App
   |
   v
Lesson Package Builder
   |
   v
Prompt Engine
   |
   v
Content Engine
   |
   +--> Gamma Engine
   +--> Quiz Engine
   +--> Activities Engine
   +--> Recap Engine
   |
   v
Workbook / Lesson Package
   |
   v
Publisher Engine
   |
   v
Rono Publisher
   |
   v
Moodle
```

------------------------------------------------------------------------

# Moodle Publishing Structure

The curriculum hierarchy is mapped to Moodle as follows:

``` text
Course
|
+-- Section: Language
    |             <- Strand
    |
    +-- Subsection: Language for interacting with others
        |          <- Sub-strand
        |
        +-- Text & Media
        |   How We Change Our Language
        |          <- Content Description
        |
        +-- Page: Lesson 1 / Mission of the Day
        |          <- Elaboration / Lesson Content
        |
        |   +-- Page: Did You Know?
        |   |          Gamma Slides
        |   |
        |   +-- Quiz: Checking Your Thinking
        |   |
        |   +-- Page: Let's Do It
        |   |          Activities
        |   |
        |   +-- Page: What We Discovered
        |              Recap
        |
        +-- Page: Lesson 2 / Mission of the Day
            |
            +-- Page: Did You Know?
            +-- Quiz: Checking Your Thinking
            +-- Page: Let's Do It
            +-- Page: What We Discovered
```

The four supporting activities for each lesson are visually indented
beneath the main Lesson Content page.

------------------------------------------------------------------------

# Curriculum Mapping

  Curriculum element       Moodle implementation
  ------------------------ ----------------------------------------
  Strand                   Section
  Sub-strand               Moodle Subsection
  Content Description      Text & Media activity
  Elaboration / Lesson     Lesson Content Page
  Mission of the Day       Main Lesson Content
  Did You Know?            Indented Page containing Gamma content
  Checking Your Thinking   Indented Quiz activity
  Let's Do It              Indented Page activity
  What We Discovered       Indented Page activity

------------------------------------------------------------------------

# Publishing Endpoint

The new architecture uses one primary lesson publishing function:

``` text
local_rono_publisher_publish_lesson
```

One request represents one complete curriculum lesson/elaboration.

The external API validates the request and delegates Moodle operations
to internal service classes.

------------------------------------------------------------------------

# Internal Architecture

``` text
local_rono_publisher/
|
+-- classes/
|   +-- external/
|   |   +-- publish_lesson.php
|   |
|   +-- service/
|       +-- publisher.php
|       +-- section_service.php
|       +-- page_service.php
|       +-- lesson_service.php
|       +-- question_service.php
|       +-- quiz_service.php
|       +-- cache_service.php
|
+-- db/
|   +-- access.php
|   +-- services.php
|
+-- lang/
|   +-- en/
|       +-- local_rono_publisher.php
|
+-- index.php
+-- lib.php
+-- settings.php
+-- version.php
```

------------------------------------------------------------------------

# Service Responsibilities

## `publish_lesson.php`

External Moodle Web Service boundary.

Responsible for:

-   validating incoming parameters;
-   validating the target course context;
-   checking `local/rono_publisher:publishlesson`;
-   calling the internal Publisher service;
-   returning Moodle IDs to the Publisher Engine.

## `publisher.php`

Coordinates publication of one complete lesson.

The intended final order is:

``` text
Find/Create Strand Section
        |
Find/Create Sub-strand Subsection
        |
Find/Create Content Description
        |
Create Lesson Content
        |
Create Did You Know?
        |
Create Question Bank Category
        |
Import Questions
        |
Create Quiz
        |
Attach Questions
        |
Create Let's Do It
        |
Create What We Discovered
        |
Rebuild Course Cache
```

## `section_service.php`

Responsible for:

-   finding or creating the Strand Section;
-   finding or creating the real Moodle Subsection for the Sub-strand;
-   returning the delegated subsection section used for lesson
    activities.

## `page_service.php`

Responsible for:

-   Content Description Text & Media activities;
-   Moodle Page creation;
-   lesson activity indentation.

## `lesson_service.php`

Responsible for lesson Page activities:

-   Lesson Content / Mission of the Day;
-   Did You Know?;
-   Let's Do It;
-   What We Discovered.

## `question_service.php`

Reserved for Moodle 5.2 Question Bank integration.

Final responsibilities:

-   create/find a dedicated Question Bank category for each lesson;
-   import generated GIFT or Moodle XML questions;
-   validate imported questions;
-   return the question references required by the Quiz service.

## `quiz_service.php`

Reserved for Moodle 5.2 Quiz integration.

Final responsibilities:

-   create Checking Your Thinking;
-   attach the questions created/imported by `question_service`;
-   place the Quiz in the correct subsection;
-   apply lesson indentation.

## `cache_service.php`

Responsible for rebuilding Moodle course caches following publishing
changes.

------------------------------------------------------------------------

# Question Bank Design

Each lesson/elaboration should have its own Question Bank category.

``` text
Content Description
|
+-- Lesson 1
|   +-- Question Bank Category
|       +-- Question 1
|       +-- Question 2
|       +-- Question 3
|
+-- Lesson 2
    +-- Question Bank Category
        +-- Question 1
        +-- Question 2
        +-- Question 3
```

Question import and Quiz assembly are deliberately separated:

``` text
GIFT / Moodle XML
        |
        v
Question Service
        |
        v
Moodle Question Bank
        |
        v
Imported Question References
        |
        v
Quiz Service
        |
        v
Checking Your Thinking
```

The Quiz service must not parse GIFT/XML itself.

------------------------------------------------------------------------

# Current Development Stage

The plugin is currently being rebuilt from scratch for the new
publishing architecture.

The structural publishing stage covers:

-   Strand Section;
-   real Moodle Subsection;
-   Content Description Text & Media;
-   Lesson Content Page;
-   Did You Know? Page;
-   Let's Do It Page;
-   What We Discovered Page;
-   activity indentation.

Question Bank and Quiz integration are the next implementation stage and
must be validated specifically against Moodle 5.2 before being treated
as production-ready.

------------------------------------------------------------------------

# Installation

The Moodle plugin directory must be:

``` text
moodle/local/rono_publisher/
```

The Moodle component name must remain:

``` text
local_rono_publisher
```

After copying the plugin into Moodle, the normal Moodle plugin
installation/upgrade process must be run and caches purged as
appropriate for the Moodle environment.

------------------------------------------------------------------------

# Security

The plugin defines the course-context capability:

``` text
local/rono_publisher:publishlesson
```

The external publishing function validates the target course context and
requires this capability before publishing lesson content.

------------------------------------------------------------------------

# Important Architecture Rule

Rono Publisher is a **publishing layer**, not an AI-generation engine.

It receives prepared curriculum content and is responsible for
converting that content into the agreed Moodle structure.

The Publisher Engine remains responsible for orchestrating the upstream
generated lesson package.

------------------------------------------------------------------------

# Copyright

Rono's School

Copyright © Mohammad Hassan

# Changelog

All notable changes to the Rono Publisher Moodle plugin.

------------------------------------------------------------------------

# New Rono Publisher Architecture

## Component

``` text
local_rono_publisher
```

The Moodle publishing plugin is being rebuilt around a lesson-level
publishing architecture designed for the Rono's School AI Curriculum
Platform.

------------------------------------------------------------------------

## Architecture Change

The publishing model is now based on one complete curriculum
lesson/elaboration rather than independent page and quiz publishing
operations.

Primary external function:

``` text
local_rono_publisher_publish_lesson
```

The external endpoint delegates Moodle implementation work to focused
internal services.

------------------------------------------------------------------------

## Moodle Curriculum Hierarchy

The agreed publishing hierarchy is:

``` text
Course
|
+-- Section
|   Strand
|
+-- Subsection
    Sub-strand
    |
    +-- Text & Media
    |   Content Description
    |
    +-- Lesson Content Page
        Mission of the Day
        |
        +-- Did You Know? Page
        |   Gamma content
        |
        +-- Checking Your Thinking
        |   Quiz Activity
        |
        +-- Let's Do It Page
        |   Activities
        |
        +-- What We Discovered Page
            Recap
```

Did You Know?, Checking Your Thinking, Let's Do It, and What We
Discovered are visually indented beneath the corresponding Lesson
Content activity.

------------------------------------------------------------------------

## New Service Architecture

Added/refactored:

``` text
classes/external/publish_lesson.php

classes/service/publisher.php
classes/service/section_service.php
classes/service/page_service.php
classes/service/lesson_service.php
classes/service/question_service.php
classes/service/quiz_service.php
classes/service/cache_service.php
```

### Publisher Service

Coordinates the complete lesson publishing operation.

### Section Service

Handles:

-   Strand Sections;
-   real Moodle Subsections for Sub-strands;
-   delegated subsection section resolution.

### Page Service

Handles:

-   Text & Media Content Description;
-   Moodle Page activities;
-   indentation.

### Lesson Service

Handles:

-   Lesson Content / Mission of the Day;
-   Did You Know?;
-   Let's Do It;
-   What We Discovered.

### Question Service

Reserved for Moodle 5.2 Question Bank integration.

It will own:

-   lesson Question Bank categories;
-   GIFT/XML import;
-   question validation;
-   question references returned to the Quiz service.

### Quiz Service

Reserved for Moodle 5.2 Quiz integration.

It will own:

-   Checking Your Thinking Quiz creation;
-   question attachment;
-   Quiz positioning and indentation.

### Cache Service

Handles course cache rebuilding.

------------------------------------------------------------------------

## External Web Service

Added:

``` text
local_rono_publisher_publish_lesson
```

The endpoint accepts one lesson/elaboration package containing:

-   course;
-   strand;
-   sub-strand;
-   content description;
-   lesson title/content;
-   Did You Know? content;
-   Quiz data;
-   activities;
-   recap.

The external class validates the course context and requires:

``` text
local/rono_publisher:publishlesson
```

------------------------------------------------------------------------

## Structural Publishing Stage

Implemented/design completed for:

-   Section from Strand;
-   Moodle Subsection from Sub-strand;
-   Text & Media from Content Description;
-   Lesson Content Page;
-   Did You Know? Page;
-   Let's Do It Page;
-   What We Discovered Page;
-   activity indentation;
-   course cache rebuilding.

The structure must be verified on Moodle before enabling Question Bank
and Quiz publishing.

------------------------------------------------------------------------

## Question Bank / Quiz Redesign

The previous quiz publishing approach is being replaced.

New intended flow:

``` text
Lesson
   |
   v
Dedicated Question Bank Category
   |
   v
Import GIFT / Moodle XML
   |
   v
Validate Imported Questions
   |
   v
Create Checking Your Thinking Quiz
   |
   v
Attach Imported Questions
```

Question importing and Quiz assembly are intentionally separate
responsibilities.

Each lesson/elaboration will have its own Question Bank category.

The Moodle 5.2 Question Bank implementation remains the next integration
stage and must be validated against Moodle 5.2 before production use.

------------------------------------------------------------------------

## Plugin Cleanup

Component naming standardized to:

``` text
local_rono_publisher
```

Language file standardized to:

``` text
lang/en/local_rono_publisher.php
```

Old `local_rono_curriculumbuilder` dependencies are being removed from
the new plugin.

`lib.php` and `settings.php` have been reduced to clean plugin-specific
implementations.

The plugin status page has been redesigned for Rono Publisher.

------------------------------------------------------------------------

## Current Status

Structural plugin build in progress.

Next milestones:

1.  Install structural-test plugin in Moodle.
2.  Verify Section and real Subsection creation.
3.  Verify Content Description placement.
4.  Verify lesson activity ordering and indentation.
5.  Implement Moodle 5.2 Question Bank service.
6.  Implement Quiz service.
7.  Test one complete lesson.
8.  Test multiple elaborations under one Content Description.
9.  Connect the working plugin to the Publisher Engine.

------------------------------------------------------------------------

# Copyright

Rono's School

Copyright © Mohammad Hassan

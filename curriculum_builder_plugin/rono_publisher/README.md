# Rono Curriculum Builder

## Moodle Plugin

**Component**

```
local_rono_curriculumbuilder
```

**Plugin Type**

```
Local Plugin
```

**Version**

```
4.0.0
```

**Author**

Mohammad Hassan

---

# Purpose

The Rono Curriculum Builder plugin is the Moodle publishing layer for the
Rono's School AI Curriculum Platform.

The plugin receives publishing requests from the Publisher Engine and creates
or updates Moodle learning resources.

The plugin **does not generate AI content**.

All AI generation occurs inside the Curriculum Builder platform.

---

# Platform Architecture

```
Teacher
      │
      ▼
Build App
      │
      ▼
Lesson Package Builder
      │
      ▼
Prompt Engine
      │
      ▼
AI Engine
      │
      ▼
Gamma Engine
      │
      ▼
Quiz Engine
      │
      ▼
Activities Engine
      │
      ▼
Recap Engine
      │
      ▼
Workbook
      │
      ▼
Publisher Engine
      │
      ▼
Rono Curriculum Builder Plugin
      │
      ▼
Moodle
```

---

# Responsibilities

The plugin is responsible for

- Course creation
- Section creation
- Moodle Page publishing
- Moodle Quiz publishing
- Page updates
- Quiz updates
- Health monitoring

The plugin is **not responsible** for

- AI generation
- Workbook reading
- Prompt generation
- Gamma presentations
- Quiz generation
- Activities generation
- Recap generation

Those responsibilities belong to the Publisher Engine.

---

# External Web Services

```
health
```

```
ping
```

```
publish_course
```

```
publish_section
```

```
publish_page
```

```
publish_quiz
```

```
publish_lesson
```

---

# Internal Components

```
repository/

page_repository.php

quiz_repository.php
```

---

# Installation

Copy

```
local_rono_curriculumbuilder
```

into

```
moodle/local/
```

Run

```
php admin/cli/upgrade.php
```

Purge caches

```
php admin/cli/purge_caches.php
```

---

# Version

Plugin Version

```
4.0.0
```

Publisher Engine

```
4.0.0
```

Workbook

```
4.0
```

---

# Copyright

Rono's School

Copyright © Mohammad Hassan
# Changelog

All notable changes to the Rono Curriculum Builder plugin.

---

# Version 4.0.0

Release Date

```
2026-07-15
```

---

## Complete Architecture Freeze

The plugin has been redesigned to work with the Rono's School AI Platform.

The Publisher Engine now owns all publishing orchestration.

The Moodle plugin has become a lightweight publishing layer.

---

## New Architecture

```
Teacher

↓

Build App

↓

Lesson Package Builder

↓

Prompt Engine

↓

AI Engine

↓

Gamma Engine

↓

Quiz Engine

↓

Activities Engine

↓

Recap Engine

↓

Workbook

↓

Publisher Engine

↓

Rono Curriculum Builder Plugin

↓

Moodle
```

---

## New Features

### External Web Services

Added

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

Improved

```
publish_lesson
```

```
health
```

```
ping
```

---

### Repository Layer

Added

```
page_repository.php
```

```
quiz_repository.php
```

---

### Database

Added

```
local_rono_page_map
```

```
local_rono_quiz_map
```

---

### Publishing

Supports

- Mission of the Day
- Check Your Thinking
- Your Turn
- What We Discovered

Automatic

- Create
- Update
- Republishing

---

### Security

Updated capabilities.

Improved context validation.

Improved service validation.

---

### Settings

Added

- Publisher Engine URL
- Publisher Timeout
- Default Course Category

---

## Architecture Status

Frozen

No further structural redesign planned.

Future work will focus on

- Integration testing
- Moodle implementation
- Bug fixing
- Production deployment

---

# Copyright

Rono's School

Mohammad Hassan
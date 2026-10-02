# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-30

### Added

- Coordinator login and role separation between ADMIN and USER.
- Student roll with search, create, edit and per-student session history.
- Tutor roll with search, create and edit.
- Weekly availability windows per tutor, with add and remove.
- Weekly and daily schedule views.
- Tutor's own upcoming sessions view.
- Idempotent demo-data seeding on first start.
- Test suite covering auth, students, tutors, availability and schedule.
- Dockerfile and docker-compose deployment files.
- GitHub Actions CI pipeline running the test suite.

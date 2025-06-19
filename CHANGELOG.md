# Changelog

All notable changes to R3nameX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Web-based GUI interface
- Configuration file support (.r3namexrc)
- Regular expression support for advanced pattern matching
- Batch processing from CSV file

## [v2.0.0] - 2025-06-18

### Added
- 🎯 **Interactive Mode** (`-a`/`--all`): Rename all files in directories and subdirectories with per-folder customization
- 🔄 **Full Rollback Support**: Complete undo functionality for ALL operations including overwrites and backups
- 📁 **Smart Duplicate Handling**: Five strategies for filename conflicts:
  - `skip`: Skip files if destination exists
  - `suffix`: Add numeric suffix (file_1, file_2)
  - `backup`: Backup existing files before renaming
  - `overwrite`: Replace existing files (with hidden backup)
  - `ask`: Interactive prompt for each conflict (default)
- 🔍 **Missing File Detection**: Warns about gaps in number sequences before renaming
- 📝 **Comprehensive Logging**: All operations logged to `logs.log` with timestamps
- 🌐 **Auto-Update Feature** (`-u`/`--update`): Check and download updates from GitHub
- 📊 **Version Command** (`-v`/`--version`): Display version and system information
- 🎨 **Improved UI**: Better formatted output with clear sections and progress indicators
- 🛡️ **Enhanced Safety**: Preview changes before applying, automatic backups for overwrites
- 📂 **Per-Folder Rollback**: Interactive rollback with folder-by-folder control

### Changed
- Renamed main function from `rename_files` to `rename_range` for clarity
- Improved help display with better formatting and organization
- Enhanced error messages with more context
- Rollback now shows file locations (main folder vs subfolders)
- Better handling of edge cases and permissions

### Fixed
- File permission checks now happen before any operation
- Proper cleanup of empty backup directories after rollback
- Correct handling of files without extensions
- Unicode filename support improved

### Security
- Added write permission verification before operations
- Hidden backup system prevents accidental data loss
- Rollback mapping file validates data integrity

## [v1.0] - 2025-02-03

### Initial Release
- Basic batch file renaming functionality
- Custom prefix support
- Number range renaming (current range to new range)
- Simple rollback for basic rename operations
- Command-line interface
- Cross-platform support (Windows, Linux, macOS)

### Features
- Rename files with sequential numbering
- Specify custom prefixes
- Define source and target number ranges
- Basic undo functionality
- Operation logging

---

## Version History Summary

| Version | Date | Major Changes |
|---------|------|---------------|
| 2.0.0 | 2025-06-18 | Interactive mode, smart duplicates, full rollback |
| 1.0 | 2025-02-03 | Initial release with basic functionality |

## Upgrade Guide

### From 1.0 to 2.0.0
1. The rollback system is completely rewritten and incompatible with v1.0 mappings
2. Clear any existing `backup_mapping.json` files before upgrading
3. New features don't require any configuration changes
4. All v1.0 commands still work the same way

### Breaking Changes in 2.0.0
- Rollback mapping format changed (not compatible with v1.0)
- Function `rename_files` renamed to `rename_range` (internal only)

## Contributing
Please see CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the BSD 3-Clause License - see the LICENSE file for details.

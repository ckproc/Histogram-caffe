# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.7

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /home/ckp/bin/cmake

# The command to remove a file.
RM = /home/ckp/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/ckp/HistogramLoss/caffe-master

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/ckp/HistogramLoss/caffe-master

# Utility rule file for symlink_to_build.

# Include the progress variables for this target.
include CMakeFiles/symlink_to_build.dir/progress.make

CMakeFiles/symlink_to_build:
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold --progress-dir=/home/ckp/HistogramLoss/caffe-master/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Adding symlink: <caffe_root>/build -> /home/ckp/HistogramLoss/caffe-master"
	ln -sf /home/ckp/HistogramLoss/caffe-master /home/ckp/HistogramLoss/caffe-master/build

symlink_to_build: CMakeFiles/symlink_to_build
symlink_to_build: CMakeFiles/symlink_to_build.dir/build.make

.PHONY : symlink_to_build

# Rule to build all files generated by this target.
CMakeFiles/symlink_to_build.dir/build: symlink_to_build

.PHONY : CMakeFiles/symlink_to_build.dir/build

CMakeFiles/symlink_to_build.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/symlink_to_build.dir/cmake_clean.cmake
.PHONY : CMakeFiles/symlink_to_build.dir/clean

CMakeFiles/symlink_to_build.dir/depend:
	cd /home/ckp/HistogramLoss/caffe-master && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/ckp/HistogramLoss/caffe-master /home/ckp/HistogramLoss/caffe-master /home/ckp/HistogramLoss/caffe-master /home/ckp/HistogramLoss/caffe-master /home/ckp/HistogramLoss/caffe-master/CMakeFiles/symlink_to_build.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/symlink_to_build.dir/depend

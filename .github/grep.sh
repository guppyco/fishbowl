#!/bin/bash
all_rules=(
    "f-string-without-interpolation"
    "fmt"
    "inconsistent-return-statements"
    "invalid-name"
    "invalid-str-returned"
    "line-too-long"  # covered by black
    "logging-format-interpolation"
    "no-else-return"
    "no-name-in-module"
    "unnecessary-lambda"
    "redefined-argument-from-local"
    "redefined-builtin"
    "redefined-outer-name"
    "self-assigning-variable"
    "super-with-arguments"
    "too-many-ancestors"
    "too-many-branches"
    "too-many-locals"
    "too-many-nested-blocks"
    "too-many-statements"
    "unbalanced-tuple-packing"
    "undefined-loop-variable"
    "unidiomatic-typecheck"
    "pointless-string-statement"
    "useless-suppression"
    "E501"  # flake8 line-too-long
)

has_error=false

for i in "${all_rules[@]}";
  do
    ! find . -name "*.py" | xargs grep ${i} || has_error=true
  done

if ${has_error}; then
  echo "a"
  # exit 1
fi

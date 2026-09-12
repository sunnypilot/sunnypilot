"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Run openpilot's large driving models on an attached Jetson.

The transport, protocol and TensorRT server live in the standalone `jetlink`
package so other projects can reuse them. Everything here is the openpilot glue
and nothing else; backend.py is the only part core openpilot ever calls.
"""

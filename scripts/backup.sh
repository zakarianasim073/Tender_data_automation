#!/usr/bin/env bash
tar -czf backup_$(date +%F).tar.gz backend/uploads backend/outputs

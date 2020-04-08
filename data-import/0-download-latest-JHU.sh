#!/usr/bin/env bash
rm -rf jhu
git clone --depth=1 https://github.com/CSSEGISandData/COVID-19.git jhu
rm -rf jhu/.git

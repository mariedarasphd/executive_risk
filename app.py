#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Very small debug app – proves that the Streamlit runtime works.
"""

import streamlit as st

# -----------------------------------------------------------------
# Page configuration (title, layout, icon – optional)
# -----------------------------------------------------------------
st.set_page_config(page_title="Debug", layout="wide", page_icon="🚀")

# -----------------------------------------------------------------
# Simple UI – if the app runs you will see these three lines
# -----------------------------------------------------------------
st.title("🚀 Debug app – it works!")
st.write(
    "If you see this text, the Streamlit container started correctly."
)
st.caption(
    "✅ If you reach this point, the Python runtime and all dependencies are loading fine."
)

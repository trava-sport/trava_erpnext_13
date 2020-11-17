# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "trava_erpnext"
app_title = "Trava Erpnext"
app_publisher = "trava"
app_description = "Trava Erpnext System"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "belyerin@ya.ru"
app_license = "MIT"
fixtures = ["Custom Field", "Custom Script", "Property Setter", "Print Format", "Report", "Workflow", "Workflow State", "Workflow Action"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/trava_erpnext/css/trava_erpnext.css"
# app_include_js = "/assets/trava_erpnext/js/trava_erpnext.js"

# include js, css files in header of web template
# web_include_css = "/assets/trava_erpnext/css/trava_erpnext.css"
# web_include_js = "/assets/trava_erpnext/js/trava_erpnext.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "trava_erpnext/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "trava_erpnext.install.before_install"
# after_install = "trava_erpnext.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "trava_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"Sales Order": {
#         "validate": "",
#     },
# }

#"validate": "trava_erpnext.trava_erpnext.doctype.agreement.sales_order.validate",

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"trava_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"trava_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"trava_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"trava_erpnext.tasks.weekly"
# 	]
# 	"monthly": [
# 		"trava_erpnext.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "trava_erpnext.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "trava_erpnext.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "trava_erpnext.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


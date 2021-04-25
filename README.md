# USNamesAnalysis
Repo for my project to understand US baby naming trends

# Purpose

I set out to understand baby naming trends in the US. I noticed names can be associated with a cohort. As that cohort ages, the age associated with the name becomes older. This led me to the question I set out to answer in this project.

Can I predict the next top names? If I can, I could avoid giving a child a name that will become too common. Alternatively, I could give a name that will make my child seem somewhat more youthful throughout their life.

Additionally, I am setting out to be able to approximate the expected age of someone given their name. I use the period life tables to estimate how many of people with the name have passed. This obviously fails to account for migration.

# Sources

* Social Security Administration - [Baby names since the 1880](https://www.ssa.gov/oact/babynames/limits.html)
* Social Security Administration - [Period life tables](https://www.ssa.gov/oact/NOTES/as120/LifeTables_Body.html#wp1168561)

# ToDo

* Add docstrings and/or make method private
* Add code overview to readme
* Add regression tests for static_analysis.py
* Do inline ToDos

# Possible Next Analyses

* list most unisex names
* add name combining
* predict next top name
* calculate expected age
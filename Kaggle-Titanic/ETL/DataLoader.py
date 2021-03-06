import pandas as pd
import numpy as np
import re

from DataVisualisation.GraphsAndPlotsBuilder import GraphsAndPlotsBuilder

from sklearn import preprocessing

class DataLoader:

    variable = "I'm a variable"
    excluded_titles = None

    # We want display to show all of the columns, rather than skip the middle ones
    pd.set_option("display.max_columns", None)

    def exploreDataframe(self, dataframe):
        print("Info: ")
        print(dataframe.info())

        print("Column Data Types: ")
        print(dataframe.dtypes)

        print("Sample: ")
        print(dataframe.sample(20))

        print("How many nulls? ")
        print(dataframe.isnull().sum())

        print("Describe the data: ")
        print(dataframe.describe(include = "all"))

    def _correctColumnTypes(self, dataframe):

        dataframe["Cabin"] = dataframe["Cabin"].astype(str)

        return dataframe

    def _finaliseColumnTypers(self, dataframe):

        dataframe["Survived"] = dataframe["Survived"].astype(bool)
        #dataframe["Pclass"] = dataframe["Pclass"].astype(int)
        dataframe["Sex"] = dataframe["Sex"].astype(bool)
        dataframe["SibSp"] = dataframe["SibSp"].astype(int)
        dataframe["Parch"] = dataframe["Parch"].astype(int)
        dataframe["Fare"] = dataframe["Fare"].astype(float)
        dataframe["FamilyPresent"] = dataframe["FamilyPresent"].astype(bool)

        return dataframe

    def _fillNACols(self, df):
        df['Age'].fillna(df['Age'].median(), inplace=True)

        # complete embarked with mode
        #df['Embarked'].fillna(df['Embarked'].mode()[0], inplace=True)

        # complete missing fare with median
        df['Fare'].fillna(df['Fare'].median(), inplace=True)

        return df

    def _fillNACabin(self, df):

        df["RoomNum"] = df["RoomNum"].astype(int)
        df["RoomNum"] = df["RoomNum"].replace(0, df["RoomNum"].median())

        return df

    def _initialiseRows(self, dataframe):


        # Calculate each persons entourage/family size (+1 to include the person themself)
        if not "FamilySize" in dataframe.columns:
            dataframe["FamilySize"] = dataframe["SibSp"] + dataframe["Parch"] + 1

        if not "FamilyPresent" in dataframe.columns:
            dataframe["FamilyPresent"] = 1
            dataframe["FamilyPresent"].loc[dataframe["FamilySize"] > 1] = 0

        if not "Title" in dataframe.columns:
            dataframe["Title"] = dataframe["Name"].str.split(", ", expand=True)[1].str.split(".", expand=True)[0]
            dataframe["Title"] = dataframe["Title"].replace("Mlle", "Miss")
            dataframe["Title"] = dataframe["Title"].replace("Ms", "Miss")
            dataframe["Title"] = dataframe["Title"].replace("Mme", "Mrs")

        if not "RoomSide" in dataframe.columns:
            dataframe["RoomSide"] = "Unknown"

        if not "Deck" in dataframe.columns:
            dataframe["Deck"] = "Unknown"

        if not "Port" in dataframe.columns:
            dataframe["Port"] = dataframe["Embarked"]

        if not "RoomNum" in dataframe.columns:
            dataframe["RoomNum"] = 0

        return dataframe


    def _formatRows(self, row):

        if row["Sex"] == "male":
            row["Sex"] = 1
        else:
            row["Sex"] = 0

        # Drop any rows where embarked is 0 later
        if row["Embarked"] != "" and row["Embarked"] is not None and row["Embarked"]:
            row["Embarked"] = 1
        else:
            row["Embarked"] = 0

        # Get only the cabin level (A, B, C etc) where n = null (filter later)
        if row["Cabin"] != "" and row["Cabin"] is not None:
            cabinString = row["Cabin"]

            if cabinString[0].isalpha():
                row["Deck"] = cabinString[0]

            number = re.findall(r'^\D*(\d+)', cabinString)

            if not self._checkEmptyList(number):

                number = int(number[0])

                row["RoomNum"] = number

                if number % 2 == 0:
                    row["RoomSide"] = "Port"
                else:
                    row["RoomSide"] = "Starboard"

        # use excludedTitles to replace any Titles with a freq < 5 with 'Other'
        if self.excluded_titles.loc[row["Title"]] == True:
            row["Title"] = "Other"

        return row

    def getPartyStats(self, dataframe):

        dataframe["Age"] = dataframe["Age"].astype(int)
        dataframe["FamilySize"] = dataframe["FamilySize"].astype(int)

        aggregation = {
            "Age": {
                "maxPartyAge":"max",
                "avgPartyAge":"mean",
                "partyMemberCount":"count"
            },
            "FamilySize": {
                "avgPartyFamilySize":"mean",
                "maxPartyFamilySize":"max"
            }
        }

        ticketGroups = dataframe.groupby("Ticket").agg(aggregation)
        ticketGroups.columns = ticketGroups.columns.get_level_values(0)
        ticketGroups.columns = ["maxPartyAge", "avgPartyAge", "partyMemberCount", "avgPartyFamilySize", "maxPartyFamilySize"]

        dataframe = dataframe.join(other=ticketGroups, on="Ticket")

        return dataframe

    def encodeCategoricalVariables(self, dataframe):

        cols_to_transform = ["Title", "RoomSide", "Deck", "Port", "Pclass"]
        dataframe = pd.get_dummies(dataframe, columns=cols_to_transform)

        return dataframe

    def _checkEmptyList(self, theList):
        if not theList:
            return True
        else:
            return False


    def TitanicLoader(self, inputPath):
        df = pd.read_csv(inputPath, infer_datetime_format=True, encoding="utf-8")

        # print("---- Initial exploration: ----")
        # self.exploreDataframe(df)

        df = self._fillNACols(df)
        df = self._correctColumnTypes(df)
        df = self._initialiseRows(df)

        self.excluded_titles = (df["Title"].value_counts() < 5)
        df = df.apply(self._formatRows, broadcast=True, reduce=False, axis=1)

        df = self.getPartyStats(df)
        #print(df['Title'].value_counts())

        df = self.encodeCategoricalVariables(df)

        df = df.drop(["Name", "Ticket", "PassengerId", "Embarked", "Cabin"], axis=1)

        df = self._fillNACabin(df)

        df = self._finaliseColumnTypers(df)

        print("---- Post Feature Engineering exploration: ----")

        #self.exploreDataframe(df)
        #print("")


        #gb = GraphsAndPlotsBuilder()
        #gb.get_feature_correlations(df)
        #print("")

        return df


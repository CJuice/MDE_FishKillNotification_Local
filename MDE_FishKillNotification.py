r"""
Author: CJuice
"""
import PrivateInformation
from arcpy import SearchCursor
import smtplib
import datetime
import logging

# VARIABLES
    # email information
strEmailUsername_From = PrivateInformation.PrivateInformation.strEmailUsername_From
strEmailUsername_To = PrivateInformation.PrivateInformation.strEmailUsername_To
strSMTPServer = PrivateInformation.PrivateInformation.strSMTPServer
intPortNumber = PrivateInformation.PrivateInformation.intPortNumber

    # fields from feature class for email message
strUniqueIDFieldName = 'objectid'
strDateCreatedFieldName = 'CreationDate'
strUserNameEventCreatorFieldName = 'username'
strUserPhoneFieldName = 'phone'
strUserEmailFieldName = 'email'
strDeadFishCountEstimateFieldName = 'DeadFish'
lsFieldsOfInterest = [strUniqueIDFieldName
                      , strDateCreatedFieldName
                      , strUserNameEventCreatorFieldName
                      , strUserPhoneFieldName
                      , strUserEmailFieldName
                      , strDeadFishCountEstimateFieldName]

    # number of hours between the time the script is run by a chron job and the time a fish kill event was created
intHoursCheckValue = 2
dtComparisonTimeCutoffForNewEventDetection = datetime.datetime.now() - datetime.timedelta(hours=intHoursCheckValue)

    # logging information
strLOGFileName = "LOG_MDEFishKillNotificationProcess_Local.log"
tupTodayDateTime = datetime.datetime.utcnow().timetuple()
strTodayDateTimeForLogging = "{}/{}/{} UTC[{}:{}:{}]".format(tupTodayDateTime[0]
                                                          , tupTodayDateTime[1]
                                                          , tupTodayDateTime[2]
                                                          , tupTodayDateTime[3]
                                                          , tupTodayDateTime[4]
                                                          , tupTodayDateTime[5])
logging.basicConfig(filename=strLOGFileName,level=logging.INFO)
logging.info(" {} - Initiated".format(strTodayDateTimeForLogging))

    # Environment dependent variables. SERVER: Staging > Staging AppData AGS
strSDEFCPath = PrivateInformation.PrivateInformation.strSDEFCPath

# FUNCTIONALITY
    # Establish Search Cursor, check datetime, store attributes
lsFeatureClassRowAttributes_NewEvent = []
cursor = SearchCursor(strSDEFCPath)
for row in cursor:

    # compare datecreated to comparison cutoff time for "new event" detection. store attributes of new events
    if row.getValue(strDateCreatedFieldName) > dtComparisonTimeCutoffForNewEventDetection:
        lsFeatureClassRowAttributes_NewEvent.append((row.getValue(strUniqueIDFieldName)
                                                , row.getValue(strDeadFishCountEstimateFieldName)
                                                , row.getValue(strUserNameEventCreatorFieldName)
                                                , row.getValue(strUserPhoneFieldName)
                                                , row.getValue(strUserEmailFieldName)))

del cursor

# Email Info
strTO = [strEmailUsername_To]
strSubjectLineText = "New Fish Kill Event(s) Reported"
strEmailBodyText = "{} New Features -  {}'s {} were added.".format(len(lsFeatureClassRowAttributes_NewEvent)
                                                                   , strUniqueIDFieldName
                                                                   , [event[0] for event in lsFeatureClassRowAttributes_NewEvent])
message = "From: {}\nTo: {}\nSubject: {}\n\n{}\n".format(strEmailUsername_From
                                                         , ", ".join(strTO)
                                                         , strSubjectLineText
                                                         , strEmailBodyText)

    # If new features exist, send email
if len(lsFeatureClassRowAttributes_NewEvent) > 0:
    for eventTuple in lsFeatureClassRowAttributes_NewEvent:
        strNewEntryDetails = "\nOID: {}\n\tSize - {}\n\t{}, {}, {}".format(eventTuple[0]
                                                                           , eventTuple[1]
                                                                           , eventTuple[2]
                                                                           , eventTuple[3]
                                                                           , eventTuple[4])
        message = message + strNewEntryDetails
    try:
        server = smtplib.SMTP(strSMTPServer, intPortNumber)
        server.ehlo()
        server.starttls()
        server.sendmail(strEmailUsername_From, strTO, message)
        server.quit()
        logging.info("\t\tEmail generated")
    except Exception as e:
        logging.error(" Exception emailing:\n\t{}".format(e))
else:
    pass
logging.info(" complete")
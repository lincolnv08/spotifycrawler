import csv
import os

from collections import defaultdict
from countries import countries as countries_dict
from datetime import date, timedelta
from SpotifyCharts import SpotifyCharts

# 0 Position
# 1 Song Name
# 2 Artist
# 3 Streams (not in viral)
# 4 Date
# 5 Region
# 6 Song ID

def writeToCSV(overall_data, viral_data, csv_path):
    if os.path.exists(csv_path):
        os.remove(csv_path)
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(overall_data)
        writer.writerows(viral_data)

def getPeakRank(country_rank_list):
    pk = 201
    for rank in country_rank_list:
        if rank == '-':
            continue
        if rank < pk:
            pk = rank
    return pk

def getCountryRankDataViral(country_data, country, date_list):
    date_index = 0
    country_rank_list = []
    for datum in country_data:
        date = datum[3]
        while date != date_list[date_index]:
            country_rank_list.append('-')
            date_index += 1
        country_rank_list.append(int(datum[0]))
        date_index += 1
    country_rank_list.insert(0, country.title())
    country_rank_list.insert(1, getPeakRank(country_rank_list[1:]))
    return country_rank_list

def getCountryRankDataOverall(country_data, country, date_list):
    date_index = 0
    country_rank_list = []
    for datum in country_data:
        date = datum[4]
        while date != date_list[date_index]:
            country_rank_list.append('-')
            date_index += 1
        country_rank_list.append(int(datum[0]))
        date_index += 1
    country_rank_list.insert(0, country.title())
    country_rank_list.insert(1, getPeakRank(country_rank_list[1:]))
    return country_rank_list

def formatDates(date_list):
    dates_formatted = []
    for date in date_list:
        yr, mo, dy = date.split('-')
        dates_formatted.append('/'.join([mo, dy, yr]))
    return dates_formatted

def getDateList(start, end):
    s_yr, s_mo, s_dy = start.split('-')
    e_yr, e_mo, e_dy = end.split('-')
    sdate = date(int(s_yr), int(s_mo), int(s_dy))
    edate = date(int(e_yr), int(e_mo), int(e_dy))
    delta = edate - sdate
    dates = []
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        dates.append(day.isoformat())
    dates.reverse()
    return dates

def makeViralTable(match_dict, params):
    date_list = getDateList(params['start_date'], params['end_date'])
    countries = params['country_names']
    table = [['Spotify Viral Charts', 'PK'] + formatDates(date_list)]
    for country in countries:
        country_code = countries_dict[country]
        if country_code not in match_dict:
            table.append([country.title()] + (['-'] * (len(date_list) + 1)))
            continue
        country_data = match_dict[countries_dict[country]]
        table.append(getCountryRankDataViral(country_data, country, date_list))
    return table


def makeOverallTable(match_dict, params):
    date_list = getDateList(params['start_date'], params['end_date'])
    countries = params['country_names']
    table = [['Spotify Overall Charts', 'PK'] + formatDates(date_list)]
    for country in countries:
        country_code = countries_dict[country]
        if country_code not in match_dict:
            table.append([country.title()] + (['-'] * (len(date_list) + 1)))
            continue
        country_data = match_dict[countries_dict[country]]
        table.append(getCountryRankDataOverall(country_data, country, date_list))
    return table

def formatViralMatches(matches):
    match_dict = {}
    for match in matches:
        country_code = match[4]
        if country_code in match_dict:
            match_dict[country_code].append(match)
        else:
            match_dict[country_code] = [match]
    return match_dict

def formatOverallMatches(matches):
    match_dict = {}
    for match in matches:
        country_code = match[5]
        if country_code in match_dict:
            match_dict[country_code].append(match)
        else:
            match_dict[country_code] = [match]
    return match_dict

def getViralMatches(match_song, match_artist):
    file = csv.reader(open('viral_tmp.csv'), delimiter=',')
    matches = []
    for row in file:
        song = row[1].lower()
        artist = row[2].lower()
        if song.find(match_song) != -1 and row[2].lower() == match_artist:
            matches.append(row)
    return matches

def getOverallMatches(match_song, match_artist):
    file = csv.reader(open('overall_tmp.csv'), delimiter=',')
    matches = []
    for row in file:
        song = row[1].lower()
        artist = row[2].lower()
        if song.find(match_song) != -1 and row[2].lower() == match_artist:
            matches.append(row)
    return matches

def writeViralData(params):
    api = SpotifyCharts()
    output_file = params['output_file']
    start = params['start_date']
    end = params['end_date']
    countries = params['countries']
    if os.path.exists('viral_tmp.csv'):
        os.remove('viral_tmp.csv')
    for country in countries:
        api.viral50Daily('viral_tmp.csv', start, end, country)

def writeOverallData(params):
    api = SpotifyCharts()
    output_file = params['output_file']
    start = params['start_date']
    end = params['end_date']
    countries = params['countries']
    if os.path.exists('overall_tmp.csv'):
        os.remove('overall_tmp.csv')
    for country in countries:
        api.top200Daily('overall_tmp.csv', start, end, country)

def getViralData(params):
    writeViralData(params)
    matches = getViralMatches(params['song'], params['artist'])
    match_dict = formatViralMatches(matches)
    return makeViralTable(match_dict, params)

def getOverallData(params):
    writeOverallData(params)
    matches = getOverallMatches(params['song'], params['artist'])
    match_dict = formatOverallMatches(matches)
    return makeOverallTable(match_dict, params)

def getOutputFile():
    file_name = input('Provide a file name for the data output (e.g. output.csv): ')
    if file_name[-4:] != '.csv':
        raise ValueError('Please use the .csv format for your data output file.')
    return file_name

def getCountries():
    file_name = input('Provide a file with a list of countries you want data from (e.g. countries.txt): ')
    if file_name[-4:] != '.txt':
        raise ValueError('Please use the .txt format for your list of countries/regions.')
    file = open(file_name, 'r')
    countries = []
    country_names = []
    for line in file:
        country = line.rstrip().lower()
        if country not in countries_dict:
            raise ValueError('Data not available for ' + country)
        countries.append(countries_dict[country])
        country_names.append(country)
    return countries, country_names

def getDates():
    start_mo, start_day, start_yr = input('What is the start date for the data you want? (format: MM/DD/YYYY) ').split('/')
    start_date = '-'.join([start_yr, start_mo, start_day])
    if len(start_date) != 10:
        raise ValueError('Invalid date format.')
    end_mo, end_day, end_yr = input('What is the end date for the data you want? (format: MM/DD/YYYY) ').split('/')
    end_date = '-'.join([end_yr, end_mo, end_day])
    if len(end_date) != 10:
        raise ValueError('Invalid date format.')
    return (start_date, end_date)

def getArtist():
    artist = input('Who is the song\'s artist? ')
    return artist.lower()

def getSong():
    song = input('What song do you want data for? ')
    return song.lower()

def crawlSpotifyCharts():
    params = {}
    params['song']= getSong()
    params['artist'] = getArtist()
    params['start_date'], params['end_date']= getDates()
    params['countries'], params['country_names'] = getCountries()
    params['output_file'] = getOutputFile()
    overall_data = getOverallData(params)
    viral_data = getViralData(params)
    writeToCSV(overall_data, viral_data, params['output_file'])

if __name__ == '__main__':
    crawlSpotifyCharts()

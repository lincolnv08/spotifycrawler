from countries import countries as countries_dict
from fycharts import SpotifyCharts

def getOutputFile():
    file_name = input('Provide a file name for the data output: ')
    return file_name

def getCountries():
    file_name = input('Provide a file with a list of countries you want data from: ')
    file = open(file_name, 'r')
    countries = []
    for line in file:
        country = line.rstrip().lower()
        if country not in countries_dict:
            raise ValueError('Data not available for ' + country)
        countries.append(countries_dict[country])
    return countries

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
    return artist

def getSong():
    song = input('What song do you want data for? ')
    return song

def crawlSpotifyCharts():
    song = getSong()
    artist = getArtist()
    start_date, end_date = getDates()
    countries = getCountries()
    output_file = getOutputFile()

if __name__ == '__main__':
    crawlSpotifyCharts()

# Import statements
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd
import time

# Variables
COUNTRIES_INTEREST = ['Austria', 'Canada', 'France', 'Germany', 'Spain', 'United Kingdom', 'United States']
DATA_DIR = 'C:/Users/Chris/Desktop'
NAME = 'Chris Lee'
FIG_DPI = 300
WIDTH = 210
HEIGHT = 297

# Get data and create dataframe
all_data = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')
countries_all = all_data['location'].unique()
columns_interest = ['location', 'date', 'total_cases', 'new_cases', 'new_cases_smoothed', 'total_deaths', 'new_deaths',
                    'new_deaths_smoothed', 'total_cases_per_million', 'total_deaths_per_million', 'total_tests',
                    'new_tests', 'total_tests_per_thousand', 'positive_rate']
data = all_data.loc[all_data['location'].isin(COUNTRIES_INTEREST), columns_interest]
data.set_index(['location', 'date']).sort_index()
data.to_csv('{}/covid.csv'.format(DATA_DIR), index=False)

time_stamp = time.strftime('%Y-%m-%d', time.gmtime())

class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 7)
        self.cell(0, 10, 'Retrieved on: {}'.format(time_stamp), 0, 0, 'L')
        self.cell(0, 10, 'Page {}'.format(str(self.page_no())), 0, 0, 'R')

# Create all country graphs
def all_country_graphs(dpi_fig, y_value, y_label, title):
    plt.figure(figsize=(11, 5), dpi=dpi_fig)
    ax = plt.gca()
    data.groupby('location').plot(kind='line', x='date', y=y_value, ax=ax)
    plt.legend(COUNTRIES_INTEREST)
    plt.title(title, fontdict={'fontsize': 15, 'fontweight': 'bold'})
    plt.xlabel('')
    plt.ylabel(y_label)
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: '{:,}'.format(int(x))))
    plt.tight_layout()
    plt.savefig('{}/{}.png'.format(DATA_DIR, title))
    plt.close()

# Create individual country graphs
def indi_country_graphs(dpi_fig, country, y_val_bar, y_val_line, y_label, title):
    ax = data[data['location'] == country].tail(100).plot.bar(x='date', y=y_val_bar, color='blue',
                                                              label='7-Day Moving Average')
    data[data['location'] == country].tail(100).plot(kind='line', x='date', y=y_val_line, ax=ax, color='red',
                                                     linewidth=2, label='Daily Cases')
    plt.gcf().set_size_inches(11, 5)
    plt.title(title, fontdict={'fontsize': 15, 'fontweight': 'bold'})
    plt.xlabel('')
    plt.ylabel(y_label)
    plt.xticks(rotation=90, fontsize=9)
    plt.yticks(fontsize=9)
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: '{:,}'.format(int(x))))
    [l.set_visible(False) for (country, l) in enumerate(ax.xaxis.get_ticklabels()) if country % 5 != 4]
    plt.tight_layout()
    plt.savefig('{}/{} in {}.png'.format(DATA_DIR, title, country), dpi=dpi_fig)
    plt.close()

# Create individual country positive rate graph
def indi_country_rate(dpi_fig, country, y_val, y_label, title):
    data[data['location'] == country].plot(kind='line', x='date', y=y_val, color='red', linewidth=2, legend=None)
    plt.gcf().set_size_inches(6, 5)
    plt.title(title, fontdict={'fontsize': 15, 'fontweight': 'bold'})
    plt.xlabel('')
    plt.ylabel(y_label)
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.tight_layout()
    plt.savefig('{}/{} in {}.png'.format(DATA_DIR, title, country), dpi=dpi_fig)
    plt.close()

# Create individual country table
def indi_country_table(dpi_fig, country, title):
    fig = plt.figure(figsize=(5, 5), dpi=dpi_fig)
    ax = fig.add_subplot(1, 1, 1)
    table_data = data.loc[data['location'] == country, ['date', 'new_cases', 'new_tests', 'new_deaths']].tail(7)
    table_data.update(table_data[['new_cases', 'new_tests', 'new_deaths']].astype(float).applymap('{:,.0f}'.format))
    table = ax.table(cellText=table_data.values, colLabels=['$\\bf{Date}$', '$\\bf{Cases}$', '$\\bf{Tests}$',
                                                            '$\\bf{Deaths}$'],
                     colColours=['c' for x in table_data.columns], loc='center')
    table.set_fontsize(14)
    table.scale(1, 2)
    ax.axis('off')
    plt.title(title, fontdict={'fontsize': 15, 'fontweight': 'bold'})
    plt.savefig('{}/{} in {}.png'.format(DATA_DIR, title, country))
    plt.close()

# Call to create all country graphs
all_country_graphs(FIG_DPI, 'total_cases', 'Total COVID Cases', 'Total Cases by Country')
all_country_graphs(FIG_DPI, 'total_tests', 'Total COVID Tests', 'Total Tests by Country')
all_country_graphs(FIG_DPI, 'total_deaths', 'Total COVID Deaths', 'Total Deaths by Country')
all_country_graphs(FIG_DPI, 'total_cases_per_million', 'Total COVID Cases Per Million',
                   'Total Cases Per Million by Country')
all_country_graphs(FIG_DPI, 'total_tests_per_thousand', 'Total COVID Tests Per Thousand',
                   'Total Tests Per Thousand by Country')
all_country_graphs(FIG_DPI, 'total_deaths_per_million', 'Total COVID Deaths Per Million',
                   'Total Deaths Per Million by Country')

# Call to create individual country graphs
for i in COUNTRIES_INTEREST:
    indi_country_graphs(FIG_DPI, i, 'new_cases', 'new_cases_smoothed', 'Daily COVID Cases', 'Daily New Cases')
    indi_country_graphs(FIG_DPI, i, 'new_deaths', 'new_deaths_smoothed', 'Daily COVID Deaths', 'Daily New Deaths')
    indi_country_rate(FIG_DPI, i, 'positive_rate', 'Percentage', 'Test Positivity Rate')
    indi_country_table(FIG_DPI, i, 'Daily Change')

# Generate PDF
pdf = PDF()
pdf.alias_nb_pages()

# First page
pdf.add_page()
pdf.set_font('Arial', 'B', 26)
pdf.cell(0, 5, 'COVID-19 Report as of {}'.format(time_stamp), 0, 0, 'C')
pdf.set_font('Arial', 'B', 20)
pdf.set_y(20)
pdf.cell(0, 5, 'Prepared by {}'.format(NAME), 0, 0, 'C')

pdf.set_font('Arial', '', 12)
pdf.set_x(25)
pdf.set_y(40)
pdf.multi_cell(190, 7, 'The COVID-19 (SARS-CoV-2) pandemic has lead to significant human loss of life and major '
                       'disruptions to society and the economy. All countries around the world are feeling the impact '
                       'of COVID-19. This report illustrates COVID-19 statistics in countries of interest. The first '
                       'page contains total statistics over time for countries of interest. The second page contains '
                       'rates over time for countries of interest. The following pages contains individual country '
                       'statistics. COVID-19 statistics are retrieved from Our World in Data GitHub page '
                       '(https://github.com/owid/covid-19-data).', 0)

pdf.set_y(98)
pdf.set_font('Arial', 'B', 18)
pdf.cell(0, 5, 'Country Total Comparison', 0, 0, 'C')
pdf.image('{}/Total Cases by Country.png'.format(DATA_DIR), 10, 106, WIDTH-20, (HEIGHT/3)-10)
pdf.image('{}/Total Deaths by Country.png'.format(DATA_DIR), 10, 194, WIDTH-20, (HEIGHT/3)-10)

# Second page
pdf.add_page()
pdf.set_font('Arial', 'B', 18)
pdf.cell(0, 5, 'Country Rate Comparison', 0, 0, 'C')
pdf.image('{}/Total Cases Per Million by Country.png'.format(DATA_DIR), 10, 18, WIDTH-20, (HEIGHT/3)-10)
pdf.image('{}/Total Deaths Per Million by Country.png'.format(DATA_DIR), 10, 106, WIDTH-20, (HEIGHT/3)-10)
pdf.image('{}/Total Tests Per Thousand by Country.png'.format(DATA_DIR), 10, 194, WIDTH-20, (HEIGHT/3)-10)

# Country information pages
for i in COUNTRIES_INTEREST:
    pdf.add_page()
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 5, '{} COVID-19 Statistics'.format(i), 0, 0, 'C')
    pdf.image('{}/Daily New Cases in {}.png'.format(DATA_DIR, i), 10, 20, WIDTH - 20, (HEIGHT / 3) - 10)
    pdf.image('{}/Daily Change in {}.png'.format(DATA_DIR, i), WIDTH - 4 - ((HEIGHT / 3) - 10), 107,
              (HEIGHT / 3) - 10, (HEIGHT / 3) - 10)
    pdf.image('{}/Test Positivity Rate in {}.png'.format(DATA_DIR, i), 10, 107, WIDTH - 7 - ((HEIGHT / 3) - 10),
              (HEIGHT / 3) - 10)
    pdf.image('{}/Daily New Deaths in {}.png'.format(DATA_DIR, i), 10, 194, WIDTH - 20, (HEIGHT / 3) - 10)

# Last page
pdf.add_page()
pdf.set_font('Arial', 'B', 18)
pdf.cell(0, 5, 'Countries Available for Report', 0, 0, 'C')
pdf.set_font('Arial', '', 12)
pdf.set_x(5)
pdf.set_y(20)
pdf.multi_cell(190, 7, ', '.join(map(str, countries_all)), 0)

# Save report
pdf.output('{}/COVID-19 Report {}.pdf'.format(DATA_DIR, time_stamp), 'F')

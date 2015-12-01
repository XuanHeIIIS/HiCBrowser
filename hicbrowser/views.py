import sys
import os
import numpy as np
from flask import Flask, render_template, request, send_file

import os
from os.path import basename, exists


import hicexplorer.trackPlot
import hicbrowser.utilities

from ConfigParser import SafeConfigParser


config = SafeConfigParser()
config.readfp(open(sys.argv[1], 'r'))

if 'static_folder' in config._sections['general']:
    print "setting static folder to {}".format(config.get('general', 'static_folder'))
    app = Flask(__name__, static_folder=config.get('general', 'static_folder'), static_url_path="/static")
else:
    app = Flask(__name__)

if 'debug' in config._sections and config.get('general', 'debug') == 'yes':
    app.debug = True


track_file = config.get("browser", "tracks")
print track_file
trp_list = []
for track in track_file.split(" "):
    track_list = hicbrowser.utilities.parse_tracks(track)
    for temp_file_name in track_list:
        print temp_file_name
        trp_list.append(hicexplorer.trackPlot.PlotTracks(temp_file_name, fig_width=20, dpi=70))
        os.unlink(temp_file_name)

img_root = config.get('browser', 'images folder')

# initialize TAD interval tree
tads_file = config.get('general', 'TAD intervals')
global tads_intval_tree
tads_intval_tree, __, __ = hicexplorer.trackPlot.file_to_intervaltree(tads_file)

# initialize gene name to position mapping
genes = config.get('general', 'genes')

global gene2pos
gene2pos = {}

# initialize tads tracks
track_file = config.get('general', 'tracks')
tads = hicexplorer.trackPlot.PlotTracks(track_file, fig_width=40, dpi=70)

tad_img_root = config.get('general', 'images folder')


with open(genes, 'r') as fh:
    for line in fh.readlines():
        if line.startswith('browser') or line.startswith('track') or line.startswith('#'):
            continue
        chrom, start, end, name = line.strip().split("\t")[0:4]
        try:
            start = int(start)
            end = int(end)
        except ValueError:
            sys.stderr.write("Problem with line {}".format(line))
            pass
        gene2pos[name.lower()] = (chrom, start, end)



def get_TAD_for_gene(gene_name):
    """
    Returs the TAD position of a given gene name

    :param gene_name:
    :return:
    """
    gene_name = gene_name.strip().lower()
    if gene_name in gene2pos:
        # get gene position
        chrom, start, end = gene2pos[gene_name]
        tad_pos = tads_intval_tree[chrom].find(start, end)[0]

        return chrom, tad_pos.start, tad_pos.end
    else:
        return None

def get_region(region_string):
    """
    splits a region string into
    a chrom, start_region, end_region tuple
    The region_string format is chr:start-end
    """
    if region_string:
        for char in ",.;|!{}()":
            region_string = region_string.replace(char, '')
        for char in "-\t ":
            region_string = region_string.replace(char, ':')
        region = region_string.split(":")
        chrom = region[0]
        try:
            region_start = int(region[1])
        except IndexError:
            region_start = 0
        try:
            region_end = int(region[2])
        except IndexError:
            region_end = 1e15  # a huge number
        if region_start < 0:
            region_start = 0
        if region_end <= region_start:
            exit("Please check that the region end is larger than the region start.\n"
                 "Values given:\nstart: {}\nend: {}\n".format(region_start, region_end))

        return chrom, region_start, region_end

def snap_to_resolution(start, end):
    """
    given a start and end, guesses the resolution and
    snaps the start and end to the closes point
    :param start: int bp
    :param end:  int bp
    :return: start, end, resolution
    """

    assert end > start, "end smaller or equal to start"

    resolutions = np.array([10000, 50000, 100000, 500000, 1000000 ])

    # find the minimun absolute distance to 1/20 of the range (end-start) to
    # the resolution vector. argmin returns the index of the minimun value
    current_resolution = resolutions[np.abs(resolutions - (float(end - start) / 20)).argmin()]

    start -= start % current_resolution
    end -= (end % current_resolution)
    end += current_resolution
    # the number of 'current_resolution' bins between start and end has
    # to be divisible by three
    res = ((end - start) / current_resolution) % 3

    if res == 1:
        end += current_resolution
        start -= current_resolution
    elif res == 2:
        end += current_resolution

    return start, end, current_resolution

@app.route('/', methods=['GET'])
def index():
    gene_name = request.args.get('search', None)
    if gene_name:
        # see if the gene is known
        tad_pos = get_TAD_for_gene(gene_name)
        if tad_pos:
            chromosome, start, end = tad_pos
            start -= 50000
            end += 50000
            # plot
            outfile = "{}/{}_{}_{}.png".format(tad_img_root,
                                               chromosome,
                                               start,
                                               end)
            if not exists(outfile):
                tads.plot(outfile, chromosome, start, end)
            browser_url = "/browser?region={}:{}-{}".format(chromosome, start, end)
            return render_template("left-sidebar.html", image=outfile, browser_url=browser_url)

    return render_template("index.html")

@app.route('/browser', methods=['GET'])
def browser():
    html_div = '<div class="item">{}</div>'
    html_img = '<img src="{}" />'
    query = request.args.get('region', None)
    if query:
        gene_name = query.strip().lower()
        # check if the query is a valid gene name
        if gene_name in gene2pos:
            chromosome, start, end = gene2pos[gene_name]
            start -= 50000
            end += 50000
        else:
            chromosome, start, end = get_region(query.strip())
            if end - start < 100000:
                sys.stderr.write("region to small ({}bp), enlarging it.".format(end-start))
                start -= 50000
                end += 50000

        start, end, resolution  = snap_to_resolution(start, end)

        # split the interval into three parts
        split_range_length = (end - start) / 3
        ranges = [(start + x * split_range_length, start + (x+1) * split_range_length) for x in range(3)]
        tracks = []
        content = []
        for _range in ranges:
            img_code = []
            img_content = []
            for trp_idx in range(len(trp_list)):
                figure_path = "/get_image?region={}:{}-{}&id={}".format(chromosome, _range[0], _range[1], trp_idx)
                img_code.append(html_img.format(figure_path))

                figure_content_path = "/get_image?region={}:|+start+|-|+end+|&id={}".format(chromosome, trp_idx)
                img_content.append(html_img.format(figure_content_path))

            tracks.append(html_div.format("\n".join(img_code)))
            if len(content) == 0:
                content.append(html_div.format(" ".join(img_content)))

        tracks = "\n".join(tracks)
        content = " ".join(content)
        content = content.replace('"', '\\"')
        content = content.replace('|', '"')
        view_range = end - start
        prev = "?region={}:{}-{}".format(chromosome, start - view_range, end - view_range )
        next = "?region={}:{}-{}".format(chromosome, start + view_range, end + view_range )
        half_rage = view_range / 2
        center = start + half_rage
        zoom_out = "?region={}:{}-{}".format(chromosome, center - half_rage * 3, center + half_rage * 3)
        step = ranges[0][1] - ranges[0][0]
        end = ranges[-1][1]
        start = ranges[0][0]
    else:
        chromosome = ''
        start = ''
        end = ''
        figure_path = '/static/img/region_ctcf_30_50.png'

    if chromosome:
        region = "{}:{}-{}".format(chromosome, start, end)
    else:
        region = ''
        prev = None
        next = None
        zoom_out = None
        content = None
        tracks = html_div.format(html_img.format(figure_path))
        step = None
        start=start
        end=end

    return render_template("layout.html", region=region, tracks=tracks, next=next, previous=prev, out=zoom_out,
                           step=step, content=content, start=start, end=end)



@app.route('/get_image', methods=['GET'])
def get_image():
    query = request.args.get('region', None)
    id = request.args.get('id', None)
    try:
        id = int(id)
    except ValueError:
        sys.stderr.write('track id not a number')
        return None
    if query:
        query = query.strip()
        chromosome, start, end = get_region(query)

        outfile = "{}/{}_{}_{}_{}.png".format(img_root,
                                              chromosome,
                                              start,
                                              end,
                                              id)
        if not exists(outfile):
            trp_list[id].plot(outfile, chromosome, start, end)


        return send_file(os.getcwd() + "/" + outfile, mimetype='image/png')

    return None
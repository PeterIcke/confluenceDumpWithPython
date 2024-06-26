import os.path
import argparse
import logging
import myModules

"""Dump Confluence content using Python

Args:
    mode: Download mode
    site: Site to export from
    space: Space to export from
    page: Page to export
    outdir: Folder to export to (optional)
    sphinx: Sphinx compatible folder structure (optional)
    notags: Do not add tags to rst files (optional)


Returns:
    HTML and RST files inside the default or custom output folder

"""


parser = argparse.ArgumentParser()
parser.add_argument('--mode', '-m', dest='mode',
                    choices=['single', 'space', 'bylabel', 'pageprops', 'recursive'],
                    help='Chose a download mode', required=True)
parser.add_argument('--site', '-S', type=str,
                    help='Atlassian Site', required=True)
parser.add_argument('--space', '-s', type=str,
                    help='Space Key')
parser.add_argument('--page', '-p', type=int,
                    help='Page ID')
parser.add_argument('--label', '-l', type=str,
                    help='Page label')
parser.add_argument('--outdir', '-o', type=str, default='output',
                    help='Folder for export', required=False)
parser.add_argument('--sphinx', '-x', action='store_true', default=False,
                    help='Sphinx compatible folder structure', required=False)
parser.add_argument('--confluence', '-c', action='store_true', default=False,
                    help='Confluence compatible folder and file naming structure', required=False)
parser.add_argument('--tags', action='store_true', default=False,
                    help='Add labels as .. tags::', required=False)
parser.add_argument('--html', action='store_true', default=False,
                    help='Include .html file in export (default is only .rst)', required=False)
parser.add_argument('--no-rst', action='store_false', dest="rst", default=True,
                    help='Disable .rst file in export', required=False)
parser.add_argument('--showlabels', action='store_true', default=False,
                    help='Export .rst files with the page labels at the bottom', required=False)
parser.add_argument('--relativelinks', action='store_true', default=False,
                    help='Replace the a href links with relative links within the current space when exporting to html.', required=False)
parser.add_argument('--loglevel', default='debug',
                    choices=['critical', 'error', 'warning', 'info', 'debug'],
                    help='Provide logging level. Example --loglevel debug, default=warning')
parser.add_argument('--logformat',
                    help='Provide the logging format. See the documentation of the logging module for more details.')
parser.add_argument('--logfile',
                    help='Specifies the file that will be used for the logging rather than the standard output stream.')

args = parser.parse_args()
if args.logfile is None:
    logging.basicConfig(level=args.loglevel.upper(), format=args.logformat)
else:
    logging.basicConfig(level=args.loglevel.upper(), format=args.logformat, filename=args.logfile)

atlassian_site = args.site
sphinx_tags = args.tags
sphinx_compatible = args.sphinx
confluence_compatible = args.confluence

if args.mode == 'single':
    logging.info(f"Exporting a single page (Sphinx set to {args.sphinx})")
    page_id = args.page
elif args.mode == 'space':
    logging.info(f"Exporting a whole space (Sphinx set to {args.sphinx})")
    space_key = args.space
elif args.mode == 'recursive':
    logging.info(f"Exporting a single page recursively (Sphinx set to {args.sphinx})")
elif args.mode == 'bylabel':
    logging.info(f"Exporting all pages with a common label (Sphinx set to {args.sphinx})")
elif args.mode == 'pageprops':
    logging.info(f"Exporting a Page Properties page with all its children (Sphinx set to {args.sphinx})")

my_attachments = []
my_embeds = []
my_embeds_externals = []
my_emoticons = []
my_emoticons_list = []

user_name = os.environ["atlassianUserEmail"]
api_token = os.environ["atlassianAPIToken"]

logging.debug("Sphinx set to " + str(sphinx_compatible))
logging.debug(f"Confluence compatible set to : {confluence_compatible}")
atlassian_site = args.site
my_outdir_base = args.outdir
relative_links = args.relativelinks
if args.mode == 'single':
    ############
    ## SINGLE ##
    ############
    page_id = args.page
    page_name = myModules.get_page_name(atlassian_site,page_id,user_name,api_token)

    my_body_export_view = myModules.get_body_export_view(atlassian_site,page_id,
        user_name,api_token).json()
    my_body_export_view_html = my_body_export_view['body']['export_view']['value']
    my_body_export_view_title = my_body_export_view['title'].replace("/","-")\
        .replace(",","").replace("&","And").replace(":","-")

    server_url = f"https://{atlassian_site}.atlassian.net/wiki/api/v2/spaces/?limit=250"

    page_url = f"{my_body_export_view['_links']['base']}{my_body_export_view['_links']['webui']}"
    page_parent = myModules.get_page_parent(atlassian_site,page_id,user_name,api_token)
    space_key = myModules.get_page_space_key(atlassian_site,page_id,user_name,api_token)
    if relative_links:
        space_id = myModules.get_page_space_id(atlassian_site,page_id,user_name,api_token)
        all_pages_full = myModules.get_pages_from_space(atlassian_site,space_id,user_name,api_token)
        all_pages_short = []
        i = 0
        for n in all_pages_full:
            i = i + 1
            all_pages_short.append({
                'page_id' : n['id'],
                'pageTitle' : n['title'],
                'parentId' : n['parentId'],
                'space_id' : n['spaceId'],
                }
            )

    if confluence_compatible:
        my_outdir_base = os.path.join(my_outdir_base,space_key)
    else:
        my_outdir_base = os.path.join(my_outdir_base,f"{page_id}-{my_body_export_view_title}")        # sets outdir to path under page_name
    my_outdir_content = my_outdir_base

#    if args.sphinx is False:
#        my_outdir_base = os.path.join(my_outdir_base,f"{page_id}-{my_body_export_view_title}")        # sets outdir to path under page_name
#        my_outdir_content = my_outdir_base
#    else:
#        my_outdir_content = my_outdir_base
    my_outdirs = []
    my_outdirs = myModules.mk_outdirs(my_outdir_base, page_id, confluence_compatible)               # attachments, embeds, scripts
    my_page_labels = myModules.get_page_labels(atlassian_site,page_id,user_name,api_token)
    logging.debug(f"Base export folder is \"{my_outdir_base}\" and the Content goes to \"{my_outdir_content}\"")
    myModules.dump_html(atlassian_site,space_key,my_body_export_view_html,my_body_export_view_title,page_id,my_outdir_base, my_outdir_content,my_page_labels,page_parent,user_name,api_token,sphinx_compatible,sphinx_tags,arg_html_output=args.html,arg_rst_output=args.rst,arg_space_pages_short=(all_pages_short if relative_links else []),arg_confluence_compatible=confluence_compatible)
    logging.info("Done!")

if args.mode == 'recursive':
    ###############
    ## RECURSIVE ##
    ###############
    page_id = args.page
    page_name = myModules.get_page_name(atlassian_site,page_id,user_name,api_token)

    my_body_export_view = myModules.get_body_export_view(atlassian_site,page_id,
        user_name,api_token).json()
    my_body_export_view_html = my_body_export_view['body']['export_view']['value']
    my_body_export_view_title = my_body_export_view['title'].replace("/","-")\
        .replace(",","").replace("&","And").replace(":","-")

    server_url = f"https://{atlassian_site}.atlassian.net/wiki/api/v2/spaces/?limit=250"

    page_url = f"{my_body_export_view['_links']['base']}{my_body_export_view['_links']['webui']}"
    page_parent = myModules.get_page_parent(atlassian_site,page_id,user_name,api_token)
    space_key = myModules.get_page_space_key(atlassian_site,page_id,user_name,api_token)
    space_id = myModules.get_page_space_id(atlassian_site,page_id,user_name,api_token)
    all_pages_full = myModules.get_pages_from_space(atlassian_site,space_id,user_name,api_token)
    all_pages_short = []
    for n in all_pages_full:
        all_pages_short.append({
            'page_id' : n['id'],
            'pageTitle' : n['title'],
            'parentId' : n['parentId'],
            'space_id' : n['spaceId'],
            }
        )

    if confluence_compatible:
        my_outdir_base = os.path.join(my_outdir_base,space_key)
    else:
        my_outdir_base = os.path.join(my_outdir_base,f"{page_id}-{my_body_export_view_title}")        # sets outdir to path under page_name
    my_outdir_content = my_outdir_base

#    if args.sphinx is False:
#        my_outdir_base = os.path.join(my_outdir_base,f"{page_id}-{my_body_export_view_title}")        # sets outdir to path under page_name
#        my_outdir_content = my_outdir_base
#    else:
#        my_outdir_content = my_outdir_base
    my_outdirs = []
    my_outdirs = myModules.mk_outdirs(my_outdir_base, page_id, confluence_compatible)               # attachments, embeds, scripts
    my_page_labels = myModules.get_page_labels(atlassian_site,page_id,user_name,api_token)
    logging.debug(f"Base export folder is \"{my_outdir_base}\" and the Content goes to \"{my_outdir_content}\"")
    
    all_pages_recursive = []
    for p in all_pages_short:
        if p['page_id'] == str(page_id):        
            def get_child_pages(arg_page_id):
                children = []
                child_pages = list(filter (lambda x: x['parentId'] == arg_page_id, all_pages_short))
                for child_page in child_pages:
                    # Add the children of the provided page id.
                    children.append(child_page)
                    # Get the children of the child page.
                    child_page_id = child_page['page_id']
                    child_pages = list(filter (lambda x: x['parentId'] == child_page_id, all_pages_short))
                    [children.append(x) for x in child_pages if x not in children]
                    # Get the recursive children of the current child page.
                    [children.append(x) for x in get_child_pages(child_page_id) if x not in children]
                return children
            all_pages_recursive = get_child_pages(p['page_id'])
            all_pages_recursive.append(p)

    page_counter = 0
    for p in all_pages_recursive:
        page_counter = page_counter + 1
        my_body_export_view = myModules.get_body_export_view(atlassian_site,p['page_id'],user_name,api_token).json()
        my_body_export_view_html = my_body_export_view['body']['export_view']['value']
        my_body_export_view_name = p['pageTitle']
        my_body_export_view_title = p['pageTitle']
        logging.debug("")
        logging.debug(f"Getting page #{page_counter}/{len(all_pages_short)}, {my_body_export_view_title}, {p['page_id']}")
        my_body_export_view_labels = myModules.get_page_labels(atlassian_site,p['page_id'],user_name,api_token)
        #my_body_export_view_labels = ",".join(myModules.get_page_labels(atlassian_site,p['page_id'],user_name,api_token))
        mypage_url = f"{my_body_export_view['_links']['base']}{my_body_export_view['_links']['webui']}"
        logging.debug(f"dump_html arg sphinx_compatible = {sphinx_compatible}")
        myModules.dump_html(atlassian_site,space_key,my_body_export_view_html,my_body_export_view_title,p['page_id'],my_outdir_base,my_outdir_content,my_body_export_view_labels,p['parentId'],user_name,api_token,sphinx_compatible,sphinx_tags,arg_html_output=args.html,arg_rst_output=args.rst,arg_space_pages_short=(all_pages_short if relative_links else []),arg_confluence_compatible=confluence_compatible)
    logging.info("Done!")

elif args.mode == 'space':
    ###########
    ## SPACE ##
    ###########
    all_spaces_full = myModules.get_spaces_all(atlassian_site,user_name,api_token)         # get a dump of all spaces
    all_spaces_short = []                                                             # initialize list for less detailed list of spaces
    i = 0
    for n in all_spaces_full:
        i = i +1
        all_spaces_short.append({                                                     # append the list of spaces
            'space_key' : n['key'],
            'space_id' : n['id'],
            'space_name' : n['name'],
            'homepage_id' : n['homepageId'],
            'spaceDescription' : n['description'],
            })
        if (n['key'] == space_key) or n['key'] == str.upper(space_key) or n['key'] == str.lower(space_key):
            logging.debug("Found space: " + n['key'])
            space_id = n['id']
            space_name = n['name']
            current_parent = n['homepageId']
    if confluence_compatible:
        my_outdir_content = os.path.join(my_outdir_base,space_key)
    else:
        my_outdir_content = os.path.join(my_outdir_base,f"{space_id}-{space_name}")
    if not os.path.exists(my_outdir_content):
        os.mkdir(my_outdir_content)
    if args.sphinx is False:
        my_outdir_base = my_outdir_content

    #logging.debug("my_outdir_base: " + my_outdir_base)
    #logging.debug("my_outdir_content: " + my_outdir_content)

    if space_key == "" or space_key is None:                                          # if the supplied space key can't be found
        logging.warn("Could not find Space Key in this site")
    else:
        space_title = myModules.get_space_title(atlassian_site,space_id,user_name,api_token)
        #
        # get list of pages from space
        #
        all_pages_full = myModules.get_pages_from_space(atlassian_site,space_id,user_name,api_token)
        all_pages_short = []
        i = 0
        for n in all_pages_full:
            i = i + 1
            all_pages_short.append({
                'page_id' : n['id'],
                'pageTitle' : n['title'],
                'parentId' : n['parentId'],
                'space_id' : n['spaceId'],
                }
            )

        # Make an index.html file
        if args.html == True:
            myModules.dump_index_file(all_pages_full, my_outdir_content, space_key, sphinx_compatible, confluence_compatible)

        # put it all together
        logging.debug(f"{len(all_pages_short)} pages to export")
        page_counter = 0
        for p in all_pages_short:
            page_counter = page_counter + 1
            my_body_export_view = myModules.get_body_export_view(atlassian_site,p['page_id'],user_name,api_token).json()
            my_body_export_view_html = my_body_export_view['body']['export_view']['value']
            my_body_export_view_name = p['pageTitle']
            my_body_export_view_title = p['pageTitle']
            logging.debug("")
            logging.debug(f"Getting page #{page_counter}/{len(all_pages_short)}, {my_body_export_view_title}, {p['page_id']}")
            my_body_export_view_labels = myModules.get_page_labels(atlassian_site,p['page_id'],user_name,api_token)
            #my_body_export_view_labels = ",".join(myModules.get_page_labels(atlassian_site,p['page_id'],user_name,api_token))
            mypage_url = f"{my_body_export_view['_links']['base']}{my_body_export_view['_links']['webui']}"
            logging.debug(f"dump_html arg sphinx_compatible = {sphinx_compatible}")
            myModules.dump_html(atlassian_site,space_key,my_body_export_view_html,my_body_export_view_title,p['page_id'],my_outdir_base,my_outdir_content,my_body_export_view_labels,p['parentId'],user_name,api_token,sphinx_compatible,sphinx_tags,arg_html_output=args.html,arg_rst_output=args.rst,arg_space_pages_short=(all_pages_short if relative_links else []),arg_confluence_compatible=confluence_compatible)
    logging.debug("Done!")
elif args.mode == 'pageprops':
    ###############
    ## PAGEPROPS ##
    ###############
    my_page_properties_children = []
    my_page_properties_children_dict = {}

    page_id = args.page
    space_key = myModules.get_page_space_key(atlassian_site,page_id,user_name,api_token)
    if relative_links:
        space_id = myModules.get_page_space_id(atlassian_site,page_id,user_name,api_token)
        all_pages_full = myModules.get_pages_from_space(atlassian_site,space_id,user_name,api_token)
        all_pages_short = []
        i = 0
        for n in all_pages_full:
            i = i + 1
            all_pages_short.append({
                'page_id' : n['id'],
                'pageTitle' : n['title'],
                'parentId' : n['parentId'],
                'space_id' : n['spaceId'],
                }
            )
    #
    # Get Page Properties REPORT
    #
    logging.debug("Getting Page Properties Report Details")
    my_report_export_view = myModules.get_body_export_view(atlassian_site,page_id,user_name,api_token).json()
    my_report_export_view_title = my_report_export_view['title'].replace("/","-").replace(",","").replace("&","And").replace(":","-")
    my_report_export_view_html = my_report_export_view['body']['export_view']['value']
    my_report_export_viewName = myModules.get_page_name(atlassian_site,page_id,user_name,api_token)
    my_report_export_view_labels = myModules.get_page_labels(atlassian_site,page_id,user_name,api_token)
    my_report_export_page_url = f"{my_report_export_view['_links']['base']}{my_report_export_view['_links']['webui']}"
    my_report_export_page_parent = myModules.get_page_parent(atlassian_site,page_id,user_name,api_token)
    my_report_export_html_filename = f"{my_report_export_view_title}.html"
        # str(my_report_export_view_title) + '.html'
    # my outdirs
    if confluence_compatible:
        my_outdir_content = os.path.join(my_outdir_base,space_key)
    else:
        my_outdir_content = os.path.join(my_outdir_base,str(page_id) + "-" + str(my_report_export_view_title))
    #logging.debug("my_outdir_base: " + my_outdir_base)
    #logging.debug("my_outdir_content: " + my_outdir_content)
    if args.sphinx is False:
        my_outdir_base = my_outdir_content

    my_outdirs = []
    my_outdirs = myModules.mk_outdirs(my_outdir_base, page_id, confluence_compatible)               # attachments, embeds, scripts
    # get info abbout children
    #my_page_properties_children = myModules.get_page_properties_children(atlassian_site,my_report_export_view_html,my_outdir_content,user_name,api_token)[0]          # list
    #my_page_properties_children_dict = myModules.get_page_properties_children(atlassian_site,my_report_export_view_html,my_outdir_content,user_name,api_token)[1]      # dict
    (my_page_properties_children,my_page_properties_children_dict) = myModules.get_page_properties_children(atlassian_site,my_report_export_view_html,my_outdir_content,user_name,api_token)
    #
    # Get Page Properties CHILDREN
    #
    page_counter = 0
    for p in my_page_properties_children:
        page_counter = page_counter + 1
        #logging.debug("Handling child: " + p)
        my_child_export_view = myModules.get_body_export_view(atlassian_site,p,user_name,api_token).json()
        my_child_export_view_html = my_child_export_view['body']['export_view']['value']
        my_child_export_view_name = my_page_properties_children_dict[p]['Name']
        my_child_export_view_labels = myModules.get_page_labels(atlassian_site,p,user_name,api_token)
        my_child_export_view_title = my_child_export_view['title']      ##.replace("/","-").replace(":","-").replace(" ","_")
        logging.debug(f"Getting Child page #{page_counter}/{len(my_page_properties_children)}, {my_child_export_view_title}, {my_page_properties_children_dict[str(p)]['ID']}")
        #logging.debug("Getting Child page #" + str(page_counter) + '/' + str(len(my_page_properties_children)) + ', ' + my_child_export_view_title + ', ' + my_page_properties_children_dict[str(p)]['ID'])
        my_child_export_page_url = f"{my_child_export_view['_links']['base']}{my_child_export_view['_links']['webui']}"
        #my_child_export_page_url = str(my_child_export_view['_links']['base']) + str(my_child_export_view['_links']['webui'])
        my_child_export_page_parent = myModules.get_page_parent(atlassian_site,p,user_name,api_token)
        html_file_name = (f"{my_page_properties_children_dict[p]['Name']}.html").replace(":","-").replace(" ","_")
        #html_file_name = my_page_properties_children_dict[p]['Name'].replace(":","-").replace(" ","_") + '.html'
        my_page_properties_children_dict[str(p)].update({"Filename": html_file_name})

        myModules.dump_html(
                arg_site=atlassian_site,
                arg_space_key=space_key,
                arg_html=my_child_export_view_html,
                arg_title=my_child_export_view_title,
                arg_page_id=p,
                arg_outdir_base=my_outdir_base,
                arg_outdir_content=my_outdir_content,
                arg_page_labels=my_child_export_view_labels,
                arg_page_parent=my_child_export_page_parent,
                arg_username=user_name,
                arg_api_token=api_token,
                arg_sphinx_compatible=sphinx_compatible,
                arg_sphinx_tags=sphinx_tags,
                arg_type="reportchild",
                arg_html_output=args.html,
                arg_rst_output=args.rst,
                arg_show_labels=args.showlabels,
                arg_space_pages_short=(all_pages_short if relative_links else []),
                arg_confluence_compatible=confluence_compatible
            )                  # creates html files for every child
    myModules.dump_html(
            arg_site=atlassian_site,
            arg_space_key=space_key,
            arg_html=my_report_export_view_html,
            arg_title=my_report_export_view_title,
            arg_page_id=page_id,
            arg_outdir_base=my_outdir_base,
            arg_outdir_content=my_outdir_content,
            arg_page_labels=my_report_export_view_labels,
            arg_page_parent=my_report_export_page_parent,
            arg_username=user_name,
            arg_api_token=api_token,
            arg_sphinx_compatible=sphinx_compatible,
            arg_sphinx_tags=sphinx_tags,
            arg_type="report",
            arg_html_output=args.html,
            arg_rst_output=args.rst,
            arg_show_labels=args.showlabels,
            arg_space_pages_short=(all_pages_short if relative_links else []),
            arg_confluence_compatible=confluence_compatible
        )         # finally creating the HTML for the report page
    logging.info("Done!")
else:
    logging.error("No script mode defined in the command line")

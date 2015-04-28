__author__ = 'Shuo Yu'

vuln_dict = {} # {prod_ver: [list of (cvd_id, score)]}}
prod_ver_dict = {} # {product: [list of versions]}

cur = ""  # cur is the database cursor pointing to the NVD table, returning `cvd_id`, `product`, `version`, `Score`

for r in cur:
    # r[0]: cvd_id, r[1]: product, r[2]: version. r[3]: score
    cvd_id, product, version, score = r

    product_version = '_'.join((product, version)) # use _ to concatenate product and version as the key used in vuln_dict

    if product_version not in vuln_dict:
        vuln_dict[product_version] = [(cvd_id, score)] # initialize the item using a list containing a tuple
    else:
        vuln_dict[product_version].append((cvd_id, score)) # otherwise add the tuple to the list

    if product not in prod_ver_dict:
        prod_ver_dict[product] = [version]
    else:
        prod_ver_dict[product].append(version)

# In this way, when you get a product, you can check all available versions for that product through prod_ver_dict;
# With a specific product-version pair, all available vulns can be retrieved through vuln_dict.
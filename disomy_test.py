import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import rpy2.robjects as robjects

def create_merge_list(directory):
    #list all files in the directory
    files = os.listdir(directory)
    
    #filter only files .ped
    ped_files = [f for f in files if f.endswith('.ped')]
    
    #check how many file .ped are
    if len(ped_files) > 1:
        #create merge.list file
        with open(os.path.join(directory, 'merge.list'), 'w') as merge_file:
            for ped_file in ped_files[1:]: #starting from the second .ped
                map_file = ped_file.replace('.ped', '.map')
                merge_file.write(f"{os.path.join(directory, ped_file)} {os.path.join(directory, map_file)}\n")
    else:
        print("WARNING: No needed to merge PLINK files!")

def merge_fam(directory):

    files = os.listdir(directory)
    ped_files = [f for f in files if f.endswith('.ped')] 
    
    merge_list_path = os.path.join(directory, 'merge.list')
    
    #check if file merge.list exists
    if os.path.isfile(merge_list_path):
    # PLINK commnand to merge files
        plink_command = f"""plink --file {os.path.join(directory, ped_files[0].split('.')[0])} \
                                    --merge-list {merge_list_path} \
                                    --make-bed \
                                    --out {os.path.join(directory, 'binary_file')}
        """
        result = subprocess.run(plink_command, shell=True, capture_output=True, text=True)
    
        #print erros and console output
        #print("Output:", result.stdout)
        #print("Errors:", result.stderr)
    else:
        plink_command = f"""plink --file {os.path.join(directory, ped_files[0].split('.')[0])} \
                                    --make-bed \
                                    --out {os.path.join(directory, 'binary_file')}
        """
        result = subprocess.run(plink_command, shell=True, capture_output=True, text=True)

def update_ids(directory, fid, iid, father_id, mother_id):
    
    fam_file_path = os.path.join(directory, 'binary_file.fam')
    
    #check if file .fam exists
    if not os.path.isfile(fam_file_path):
        print("ERROR: file binary_file.fam not found.")
        return

    #update .fam with proband information
    updated_fam_lines = [] 
    with open(fam_file_path, 'r') as fam_file: 
        for line in fam_file: 
            fields = line.strip().split() 
            fields[0] = fid
            if fields[1] == iid: 
                fields[2] = father_id 
                fields[3] = mother_id
            if fields[1] == father_id: 
                fields[4] = '1'
            if fields[1] == mother_id: 
                fields[4] = '2' 
            updated_fam_lines.append(' '.join(fields)) 
              
    with open(fam_file_path, 'w') as fam_file: 
            for line in updated_fam_lines: 
                fam_file.write(line + '\n')

def mendel_check(directory):

    files = os.listdir(directory)
    binary_file = [f for f in files if f.endswith('binary_file.bed')] 
    
    # PLINK commnand to merge files
    plink_command = f"""plink --bfile {os.path.join(directory, binary_file[0].split('.')[0])} \
                            --mendel \
                            --out {os.path.join(directory, 'mendel_check')}
    """
    result = subprocess.run(plink_command, shell=True, capture_output=True, text=True)
        
    #print erros and console output
    #print("Output:", result.stdout)
    #print("Errors:", result.stderr)

def add_coords(directory):

    files = os.listdir(directory)

    mendel_path = [f for f in files if f.endswith('mendel_check.mendel')][0] 
    bim_path = [f for f in files if f.endswith('binary_file.bim')][0]

    mendel_df = pd.read_csv(os.path.join(directory, mendel_path), sep='\s+', header=None, skiprows=1, usecols=[2, 3])
    bim_df = pd.read_csv(os.path.join(directory, bim_path), sep='\s+', header=None, usecols=[1, 3], names=["SNP", "pos"])
    
    merged_df = pd.merge(mendel_df, bim_df, left_on=mendel_df.columns[1], right_on="SNP", how="left")
    
    cols = merged_df.columns.tolist()
    merged_df = merged_df[cols]

    merged_df.drop(columns=["SNP"], inplace=True)
    merged_df.rename(columns={2: 'chr', 3: 'rs_id', 'pos': 'start'}, inplace=True)
    merged_df['end'] = merged_df['start']
    cols = ['chr', 'start', 'end', 'rs_id'] 
    merged_df = merged_df[cols]
    merged_df['chr'] = 'chr' + merged_df['chr'].astype(str)

    merged_df.to_csv(os.path.join(directory, 'mendel_check.csv'), sep=';', index=False)

    #count errors per chromosome   
    sorted_df = merged_df.groupby('chr').size().reset_index(name = 'count').sort_values(by='count', ascending=False)
    total_count = sorted_df['count'].sum()

    sorted_df['prop'] = sorted_df['count']/total_count
    chr_to_plot = sorted_df[sorted_df['prop'] > 0.5]['chr']

    filtered_df = merged_df[merged_df['chr'].isin(chr_to_plot)]

    filtered_df.to_csv(os.path.join(directory, 'plot_chr.csv'), sep=';', index=False)
    
def create_pie_chart(directory):
    # load csv file
    df = pd.read_csv(os.path.join(directory, 'mendel_check.csv'), sep=';')
    
    # count number of mendelian erros by chromosome
    counts = df.groupby(df.columns[0]).size()
    
    # create a pie chart
    plt.figure(figsize=(10, 7))
    plt.pie(counts, labels=counts.index, startangle=140, labeldistance=1.05)
    plt.title('Proportion of Mendelian Errors per chromosome')
    
    #make it a donut chart
    centre_circle = plt.Circle((0,0), 0.70, fc='white') 
    fig = plt.gcf() 
    fig.gca().add_artist(centre_circle)

    #save the plot
    plt.savefig(os.path.join(directory, 'donut_chart.png'))
    plt.close()

    # Caminho para o script R
    #r_script_path = 'plot_idiogram.R'

    # B sure that Rscript is in the PATH
    #command = ['Rscript', r_script_path, directory]

    # Executar o comando
    #result = subprocess.run(command, capture_output=True, text=True)

    # Verificar a saída e erros
    #print("Output:", result.stdout)
    #print("Errors:", result.stderr)

def plot_idiogram(directory):
    r_code = f"""
    if (!require("karyoploteR", quietly = TRUE))
      BiocManager::install("karyoploteR", 
                           ask = FALSE,
                           verbose = FALSE)

    args = c("{directory}")

    mendel_check = readr::read_csv2(paste0(args[1], "/plot_chr.csv"))

    mendel_check_bed = mendel_check |> 
      regioneR::toGRanges(y = NA)

    png(filename = paste0(args[1], "/idiogram.png"), 
        width = 800, 
        height = 600)
    p1 = karyoploteR::plotKaryotype(genome="hg19",
                               plot.type = 1,
                               chromosomes = unique(mendel_check$chr)) |>
      karyoploteR::kpPoints(mendel_check_bed,
                            data.panel = 1,
                            pch = 15,
                            y = 0.001,
                            cex = 0.5)
    dev.off()
    """

    # Executa o código R
    robjects.r(r_code)

def main():
    parser = argparse.ArgumentParser(description="Run PLINK commands for disomy tests.")
    parser.add_argument('--directory', type=str, default='.', help="Directory containing the .ped files. Default is the current directory.")
    parser.add_argument('fid', type=str, help="New family ID.")
    parser.add_argument('iid', type=str, help="New within-family ID.")
    parser.add_argument('father_id', type=str, help="New paternal within-family ID.")
    parser.add_argument('mother_id', type=str, help="New maternal within-family ID.")
    
    args = parser.parse_args()
    
    create_merge_list(args.directory)
    merge_fam(args.directory)
    update_ids(args.directory, args.fid, args.iid, args.father_id, args.mother_id)
    mendel_check(args.directory)
    add_coords(args.directory)
    create_pie_chart(args.directory)
    plot_idiogram(args.directory)

if __name__ == "__main__":
    main()

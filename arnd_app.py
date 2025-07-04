import pandas as pd
from requests import get
from bs4 import BeautifulSoup as bs
import re
import matplotlib.pyplot as plt 
import numpy as np
import streamlit as st
import streamlit.components.v1 as components 



st.markdown("""<style>body {background-color: #b2f7e9;} .stApp { background-color: #b2f7e9; } </style>""", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: Blue';>🕷️ SCRAPING SUR COINAFRIQUE AVEC BEAUTIFULSOUP ET WEB-SCRAPER 🕷️</h5>", unsafe_allow_html=True) 



st.markdown(""" <style> section[data-testid="stSidebar"] {background-color: #0f926d; }  
                 .sidebar-caption { position: relative; top: 200px;  font-size: 14px; text-align: center; color: white; } 
                </style> """, unsafe_allow_html=True)

st.sidebar.markdown( """ <div style='text-align: center; bottom: 30px;font-weight: bold; font-size: 20px; color: white; '>  <b> ☰  Menu</b>  </div> """, unsafe_allow_html=True)
st.markdown(""" <style>  section[data-testid="stSidebar"] label { color: white; } </style> """, unsafe_allow_html=True)

choix = st.sidebar.selectbox('Choisir une action', ['Tableau de bord','Scraper Vetements homme','Scraper Chaussures homme','Scraper Vetements enfant', 'Scraper Chaussures enfant','Télécharger les données existantes', 'Formulaire évalution'])
nbre_pages = st.sidebar.selectbox('Nombre de pages', list([int(nbr) for nbr in np.arange(1, 350)]))
nbr_articles_page = st.sidebar.number_input("Nombre max d'articles par page", min_value=5, max_value=100, value=10, step=1)
 
st.sidebar.markdown("""
<div class="sidebar-caption">
    <b><u>EXAMEN DATA COLLECTION</u></b> <br/>ABDOURAHMANE NDIAYE <br/> 📧 : ingndiaye@gmail.com
</div>
""", unsafe_allow_html=True) 
     
def charger_dataframe(dataframe,nom_fichier, titre_bt, id_bt, key_bt_dwn,type_screping) :
    st.markdown(""" <style> div.stButton {text-align:center; } </style>""", unsafe_allow_html=True)

    if st.button(titre_bt,id_bt): 

        st.write('Données "'+titre_bt+'" Scrapées avec '+type_screping) 
        st.write('Tailles des donnée: ' + str(dataframe.shape[0]) + ' ligne et ' + str(dataframe.shape[1]) + ' colonnes.')
        st.dataframe(dataframe)

st.markdown('''<style> .stButton>button {font-size: 12px; height: 3em; width: 23em;} .stButton>button:hover { background-color: #0f926d; color: white; cursor: pointer;}</style>''', unsafe_allow_html=True)

def scraper_donnees_coinaf(nbrepage,produits):
     
    data = []  

    for p in range(1,nbrepage+1):
        url = f'https://sn.coinafrique.com/categorie/{produits}?page={p}'
         
        content_page  = get(url) # récupérere le contenu code de la page
        soup = bs(content_page.text, "html.parser") # soup = le contenu de la page dans un objet beautifulSoup
         
        containers = soup.find_all('div', class_ = 'col s6 m4 l3') 

        for container in containers[:nbr_articles_page+1] :
        #for container in containers:
            try: 
                url_container = "https://sn.coinafrique.com" + container.find('a')['href']
                res_container = get(url_container)
                soup_container = bs(res_container.text, "html.parser")
                 
                #Titre de l'annonce
                detail = container.find('p', class_ = "ad__card-description").text
                 
                #Prix du produit
                try :
                     price = soup_container.find('p', class_='price').text.replace("CFA", "").replace(" ", "")
                     prix = float(price) 
                except: 
                    prix=np.nan        

                #ur de l'image
                img_brute = container.find('img', class_='ad__card-img')
                img_url = img_brute['src'] if img_brute and img_brute.has_attr('src') else None
                #Adresse
                adresse="" 
                adrbrute = soup_container.find_all('span', class_='valign-wrapper')
                for abrt in adrbrute:
                    if abrt and abrt.has_attr('data-address'): 
                        adresse = abrt['data-address'] 

                #Récupèrer le Type     
                spans_in = abrt.find_all('span')
                if len(spans_in) >= 1:
                    Type = spans_in[-1].text.strip()  
                else :
                    Type=None     

                
                dic = {
                    'Type': Type+' : '+ detail,
                    'Prix': prix,
                    'Adresse': adresse, 
                    'Url_Image': img_url
                    }
                data.append(dic)
            except:            
                pass

    DF = pd.DataFrame(data)
    return DF 

  
def nettoyerprix(prix):
    if not isinstance(prix, str):
        return np.nan 
    chiffres = re.findall(r'\d+', prix)
    if not chiffres:
        return np.nan   
    prix_nettoye = float(''.join(chiffres))
    if prix_nettoye >1000000:
        return np.nan
    return prix_nettoye


if  choix == 'Tableau de bord':
    dtfrm_chaus_enf = pd.read_csv('donnees/Chaussures_Enfant.csv', encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
    dtfrm_chaus_hom = pd.read_csv('donnees/Chaussures_Homme.csv', encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
    dtfrm_vetem_enf = pd.read_csv('donnees/Vetements_Enfant.csv', encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
    dtfrm_vetem_hom = pd.read_csv('donnees/Vetements_Homme.csv', encoding='ISO-8859-1', sep=';', on_bad_lines='skip') 
    
    #Premier graph
    dtfrm_chaus_enf['prix_nettoye'] = dtfrm_chaus_enf['prix'].apply(nettoyerprix)
    dtfrm_vetem_enf['prix_nettoye'] = dtfrm_vetem_enf['prix'].apply(nettoyerprix) 
    prix_moyen_chaus_enf = dtfrm_chaus_enf['prix_nettoye'].mean() 
    prix_moyen_vetem_enf = dtfrm_vetem_enf['prix_nettoye'].mean() 
    plot1= plt.figure(figsize=(22,10))
    bars = plt.bar(['Chaussures','Vêtements'], [prix_moyen_chaus_enf,prix_moyen_vetem_enf], color='skyblue')

    for bar in bars:
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()
        plt.text(x, y + 500, f'{y:,.0f}'.replace(',', ' ') + ' CFA', ha='center', va='center', fontsize=14, fontweight='bold')

    plt.title('Prix moyen - Enfant',fontsize=18)
    plt.xlabel('Type Articles',fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    st.pyplot(plot1)

    #Deuxieme graph
    dtfrm_chaus_hom['prix_nettoye'] = dtfrm_chaus_hom['prix'].apply(nettoyerprix)
    dtfrm_vetem_hom['prix_nettoye'] = dtfrm_vetem_hom['prix'].apply(nettoyerprix)

    prix_moyen_chaus_hom = dtfrm_chaus_hom['prix_nettoye'].mean() 
    prix_moyen_vetem_hom = dtfrm_vetem_hom['prix_nettoye'].mean() 
    plot2 = plt.figure(figsize=(22,10))
    bars1 = plt.bar(['Chaussures','Vêtements'], [prix_moyen_chaus_hom,prix_moyen_vetem_hom], color='Red')
    
    for bar in bars1:
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()
        plt.text(x, y + 500, f'{y:,.0f}'.replace(',', ' ') + ' CFA', ha='center', va='center', fontsize=14, fontweight='bold')

     
    plt.title('Prix moyen - Homme',fontsize=18)
    plt.xlabel('Type Articles',fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    st.pyplot(plot2)
 
elif choix=='Scraper Vetements homme': 
    dtfrm = scraper_donnees_coinaf(nbre_pages,'vetements-homme') 
    charger_dataframe(dtfrm,'Vetements-homme', 'Vétements pour Homme', '1', '11','BeautifulSoup')

elif choix=='Scraper Chaussures homme': 
    dtfrm = scraper_donnees_coinaf(nbre_pages,'chaussures-homme') 
    charger_dataframe(dtfrm, 'chaussures-homme','Chaussurespour Homme', '2', '12','BeautifulSoup')   
elif choix=='Scraper Vetements enfant': 
    dtfrm = scraper_donnees_coinaf(nbre_pages,'vetements-enfants') 
    charger_dataframe(dtfrm, 'vetements-enfants', 'Vetementspour enfants', '3', '13','BeautifulSoup')    

elif choix=='Scraper Chaussures enfant': 
    dtfrm = scraper_donnees_coinaf(nbre_pages,'chaussures-enfants') 
    charger_dataframe(dtfrm,'chaussures-enfants', 'Chaussures pour enfants', '4', '14','BeautifulSoup')

elif choix == 'Télécharger les données existantes': 
    dtfrm_chaus_enf = pd.read_csv('donnees/Chaussures_Enfant.csv', encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
    dtfrm_chaus_hom = pd.read_csv('donnees/Chaussures_Homme.csv', encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
    dtfrm_vetem_enf = pd.read_csv('donnees/Vetements_Enfant.csv', encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
    dtfrm_vetem_hom = pd.read_csv('donnees/Vetements_Homme.csv', encoding='ISO-8859-1', sep=';', on_bad_lines='skip') 


    charger_dataframe(dtfrm_chaus_enf, 'Chaussures_Enfant','Chaussures pour Enfant', '6', '16','Web-Scraper')
    charger_dataframe(dtfrm_vetem_enf, 'Vetements_Enfant', 'Vetements pour Enfant', '7', '17','Web-Scraper') 
    charger_dataframe(dtfrm_chaus_hom,'Chaussures_Homme', 'Chaussures pour Hommer', '8', '18','Web-Scraper')  
    charger_dataframe(dtfrm_vetem_hom,'Vetements_Homme', 'Vetements pour Homme', '5', '15','Web-Scraper')

else :
    components.html("""<iframe src="https://ee.kobotoolbox.org/single/70d6ca332ba1f4bef90ecd2d461db7a6" width="700" height="1000"</iframe>""",height=1100,width=800)

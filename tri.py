import pandas as pd

def nettoyer(val):
    """Nettoie les codes (supprime espaces et le .0 des nombres)."""
    if pd.isna(val): return ""
    v = str(val).strip()
    if v.endswith('.0'): v = v[:-2]
    return v

def executer_tri(df_base, df_data, col_sap_base, col_sap_data):
    """Logique de traitement et de tri."""
    # La colonne numéro est automatiquement la première du fichier base
    col_num_base = df_base.columns[0]
    # On utilise la même colonne dans DATA pour la destination
    col_num_data = df_data.columns[0] 

    # Préparation des clés
    df_base_copy = df_base.copy()
    df_data_copy = df_data.copy()
    
    df_base_copy['CLE_TEMP'] = df_base_copy[col_sap_base].apply(nettoyer)
    df_data_copy['CLE_TEMP'] = df_data_copy[col_sap_data].apply(nettoyer)

    # Mapping Numéro : {Code SAP -> Numéro}
    mapping_numero = dict(zip(df_base_copy['CLE_TEMP'], df_base_copy[col_num_base]))

    # Mapping Ordre : {Code SAP -> Position Index}
    ordre_base = df_base_copy['CLE_TEMP'].unique().tolist()
    mapping_ordre = {code: i for i, code in enumerate(ordre_base)}

    # Remplissage du Numéro dans DATA
    df_data_copy[col_num_data] = df_data_copy['CLE_TEMP'].map(mapping_numero)

    # Calcul de la position de tri
    df_data_copy['POSITION_TRI'] = df_data_copy['CLE_TEMP'].map(mapping_ordre).fillna(999999)

    # Tri effectif
    df_final = df_data_copy.sort_values(by='POSITION_TRI', kind='mergesort').copy()

    # Nettoyage des colonnes techniques
    df_final = df_final.drop(columns=['CLE_TEMP', 'POSITION_TRI'])
    
    return df_final
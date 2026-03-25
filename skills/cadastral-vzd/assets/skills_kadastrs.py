import geopandas as gpd # pip install geopandas
from typing import Optional
# Need to install also: huggingface-hub (to read data from hf://datasets/) and pyarrow (to read parquet file)

gdf2 = gpd.read_parquet("FISK_DZI_ZON_short.parquet")

def undivided_share(shares_owned: int, total_share: int) -> float:
    """
    Calculate the undivided share as a proportion of total shares.
    
    This function computes the ratio of shares owned to total shares,
    returning the result as a rounded decimal proportion. A small epsilon
    value is added to the denominator to prevent division by zero.
    
    Parameters
    ----------
    shares_owned : int
        The number of shares owned by an individual.
    total_share : int
        The total number of shares in the pool.
    
    Returns
    -------
    float
        The proportion of shares owned, rounded to 2 decimal places.
        Returns a value between 0.00 and 1.00 (approximately).
    """
    return round(shares_owned/(total_share+0.00001), 2)

###################### BASE VALUES #######################################

def land_base_value(land_purpose_in_city: str, value_zone: str) -> Optional[float]:
    """
    Retrieve the land base value EUR/m2 for a specific land purpose in a city in a given value zone.
    
    This function queries a GeoDataFrame (gdf2) to find the land value based on
    the specified value zone code and land purpose category within a city.
    
    Parameters
    ----------
    land_purpose_in_city : str
        The code representing the land purpose category within the city.
        Possible values:
            'PR600' ('Neapgūta individuālo dzīvojamo māju apbūves zeme'),
            'PR601' ('Individuālo dzīvojamo māju apbūve'),
            'PR700' ('Neapgūta daudzdzīvokļu māju apbūves zeme'),
            'PR701' ('Vienstāva un divstāvu daudzdzīvokļu māju apbūve'),
            'PR702' ('Trīs, četru un piecu stāvu daudzdzīvokļu māju apbūve'),
            'PR703' ('Sešu līdz sešpadsmit stāvu daudzdzīvokļu māju apbūve'),
            'PR704' ('Septiņpadsmit un vairāk stāvu daudzdzīvokļu māju apbūve').

    value_zone : str
        The zone code identifier used to filter the GeoDataFrame by the 'CODE' column.
    
    Returns
    -------
    Optional[float]
        The land base value for the specified land purpose in the given value zone in EUR/m2.
        The return type depends on the data type stored in the queried column.
    
    Notes
    -----
    This function assumes that a GeoDataFrame named 'gdf2' exists in the scope
    and contains a 'CODE' column for zone identification and columns for various
    land purposes.
    
    Examples
    --------
    >>> land_base_value('PR704', "3-0010000-010")
    498.01
    
    >>> land_base_value('UT1122', "3-0010000-030")
    320.15
    """

    lpc_codes = {'PR600': 'Neapgūta individuālo dzīvojamo māju apbūves zeme',
                 'PR601': 'Individuālo dzīvojamo māju apbūve',
                 'PR700': 'Neapgūta daudzdzīvokļu māju apbūves zeme',
                 'PR701': 'Vienstāva un divstāvu daudzdzīvokļu māju apbūve',
                 'PR702': 'Trīs, četru un piecu stāvu daudzdzīvokļu māju apbūve',
                 'PR703': 'Sešu līdz sešpadsmit stāvu daudzdzīvokļu māju apbūve',
                 'PR704': 'Septiņpadsmit un vairāk stāvu daudzdzīvokļu māju apbūve'}
    
    if land_purpose_in_city not in lpc_codes:
        valid_codes = '\n'.join([f"  - {code} ({desc})" for code, desc in lpc_codes.items()])
        raise ValueError(f"Wrong land purpose category: '{land_purpose_in_city}'.\n"
                        f"Use one of these (the meanings in Latvian are in parentheses): \n{valid_codes}")

    return gdf2[gdf2["CODE"] == value_zone][land_purpose_in_city].iloc[0]

def premises_group_base_value(usage_type: str, value_zone: str) -> Optional[float]:
    """
    Retrieve the base value of a group of premises EUR/m2 for a specific type of use of a group of premises in a city (usage_type) in a given value zone (value_zone).
    
    This function queries a GeoDataFrame (gdf2) to find the base value of a group of premises on
    the specified value zone code and type of use of a group of premises within a city.
    
    Parameters
    ----------
    usage_type : str
        The code representing the type of use of a group of premises within the city.
        Possible values:
            'UT1110' ('Viena dzīvokļa mājas dzīvojamo telpu grupa'),
            'UT1121' ('Divu dzīvokļu mājas dzīvojamo telpu grupa'),
            'UT1122' ('Triju vai vairāku dzīvokļu mājas dzīvojamo telpu grupa').

    value_zone : str
        The zone code identifier used to filter the GeoDataFrame by the 'CODE' column.
    
    Returns
    -------
    Optional[float]
        The base value of a group of premises for the specified type of use of a group of premises in the given value zone in EUR/m2.
        The return type depends on the data type stored in the queried column.
    
    Notes
    -----
    This function assumes that a GeoDataFrame named 'gdf2' exists in the scope
    and contains a 'CODE' column for zone identification and columns for various
    type of use of a group of premises.
    
    Examples
    --------
    >>> premises_group_base_value('UT1110', "3-0010000-010")
    782.58
    
    >>> premises_group_base_value('UT1121', "3-0010000-030")
    320.15
    """

    ut_codes = {'UT1110': 'Viena dzīvokļa mājas dzīvojamo telpu grupa',
                'UT1121': 'Divu dzīvokļu mājas dzīvojamo telpu grupa',
                'UT1122': 'Triju vai vairāku dzīvokļu mājas dzīvojamo telpu grupa'}
    
    if usage_type not in ut_codes:
        valid_codes = '\n'.join([f"  - {code} ({desc})" for code, desc in ut_codes.items()])
        raise ValueError(f"Wrong usage type: '{usage_type}'.\n"
                        f"Use one of these (the meanings in Latvian are in parentheses): \n{valid_codes}")

    return gdf2[gdf2["CODE"] == value_zone][usage_type].iloc[0]

###################### CADASTRAL VALUES #######################################

def land_fiscal_cadastral_value_city(land_purpose_in_city: str,
                                     value_zone: str,
                                     land_area: int,
                                     encumbrance_area: int = 0,
                                     contaminated_area: int = 0,
                                     base_value: Optional[float] = None
                                     ) -> Optional[float]:
    """
    Calculate the fiscal cadastral value (EUR) for building land and rural land in cities.
    
    This function computes the cadastral value according to Latvian regulations
    (Section 86) by applying various correction coefficients to the base land value.
    
    Parameters
    ----------
    land_purpose_in_city : str
        The code representing the land purpose category within the city.
        Possible values:
            'PR600' ('Neapgūta individuālo dzīvojamo māju apbūves zeme'),
            'PR601' ('Individuālo dzīvojamo māju apbūve'),
            'PR700' ('Neapgūta daudzdzīvokļu māju apbūves zeme'),
            'PR701' ('Vienstāva un divstāvu daudzdzīvokļu māju apbūve'),
            'PR702' ('Trīs, četru un piecu stāvu daudzdzīvokļu māju apbūve'),
            'PR703' ('Sešu līdz sešpadsmit stāvu daudzdzīvokļu māju apbūve'),
            'PR704' ('Septiņpadsmit un vairāk stāvu daudzdzīvokļu māju apbūve').
        Must be one of the valid land purpose codes defined in the system.
    value_zone : str
        The value zone code identifier used to determine the base land value.
    land_area : int
        Total land area in square meters (m²).
    encumbrance_area : int, optional
        Area affected by encumbrances in square meters (m²). Default is 0.
        Used to calculate the encumbrance correction coefficient.
    contaminated_area : int, optional
        Area designated as contaminated in square meters (m²). Default is 0.
        Used when the land has a registered "Contaminated site" encumbrance
        in the Cadastre Information System (Section 83).
    base_value : float, optional
        Override for the base land value (EUR per m²). Default is None.
        If provided, this value is used directly instead of looking up
        the base value via land_base_value(land_purpose_in_city, value_zone).

    Returns
    -------
    Optional[float]
        The calculated cadastral value in euros, rounded to 2 decimal places.
        Returns None if the calculation cannot be completed.
       
    Examples
    --------
    >>> land_fiscal_cadastral_value_city('PR601', '3-0010000-010', 1000, 100, 50)
    33793.4
    
    >>> land_fiscal_cadastral_value_city('PR700', '3-0010000-030', 500)
    5690.0
    
    See Also
    --------
    land_base_value : Function to retrieve base land values by zone and purpose

    """
    MIN_K_APGR = 1
    C = 1 # vērtību attiecības koeficients
    DIV0_FIX = 0.000001

    # zemes bāzes vērtība lietošanas mērķim euro par kvadrātmetru
    if base_value is not None:
        bv = base_value
    else:
        bv = land_base_value(land_purpose_in_city, value_zone)
    #print(f"bv: {bv}")

    # platības korekcijas koeficients
    K_samaz = 1

    # apgrūtinājumu korekcijas koeficients atbilstoši lietošanas mērķim
    K_apgr = 1
    if encumbrance_area > 0:
        K_apgr = min(MIN_K_APGR, round(encumbrance_area / (land_area + DIV0_FIX), 2))

    # piesārņojuma korekcijas koeficients
        # 83. Zemes vienībai un zemes vienības daļai, kurai Kadastra informācijas sistēmā reģistrēts apgrūtinājums "Piesārņota vieta"..
    K_p = min(1, round(1 - contaminated_area / (land_area + DIV0_FIX), 2))
    #print(f"K_p: {K_p}")

    # 86. Kadastrālo vērtību apbūves zemei un lauku zemei pilsētās aprēķina, izmantojot šādu formulu:
    return round(bv * land_area * K_samaz * K_apgr * K_p * C, 2)

def group_premises_fiscal_cadastral_value_city(usage_type: str,
                                               value_zone: str,
                                               premises_area: float, # kopējā platība (t.sk. ārtelpu)
                                               outdoor_area: float = 0, # ārtelpu kopējā platība
                                               is_utility_room: bool = False, # Saimniecības telpu grupa
                                               is_residential_premises: bool = False, # Dzīvojamo telpu grupa
                                               is_non_residential_premises: bool = False, # Nedzīvojamo telpu grupa
                                               floor: int = 2, # < 1 - pagrabs; default 2 - lai K_st būtu 1
                                               is_sewer: bool = True, # kanalizācija
                                               is_sanitary_unit: bool = True, # sanitārais mezgls
                                               is_heating: bool = True, # apkure
                                               base_value: Optional[float] = None
                                               ) -> Optional[float]:
    """
    Calculate the cadastral value for a premises group in a multifunctional building.
    
    This function computes the cadastral value according to Latvian regulations
    (Section 136) for premises groups in multifunctional buildings by applying
    various correction coefficients to the base premises value.
    
    Parameters
    ----------
    usage_type : str
        The premises usage type code (e.g., 'PR601', 'PR700').
        Must be one of the valid usage type codes defined in the system.
        Possible values:
            'UT1110' ('Viena dzīvokļa mājas dzīvojamo telpu grupa'),
            'UT1121' ('Divu dzīvokļu mājas dzīvojamo telpu grupa'),
            'UT1122' ('Triju vai vairāku dzīvokļu mājas dzīvojamo telpu grupa').
    value_zone : str
        The value zone code identifier used to determine the base premises value
        (e.g., '3-0010000-010', '3-0010000-030').
    premises_area : float
        Total premises area in square meters (m²), including outdoor areas.
    outdoor_area : float, optional
        Total outdoor area in square meters (m²). Default is 0.
        If provided, the total area will be adjusted according to Section 137
        using the outdoor area correction coefficient (C_OUTDOOR = 0.3).
    is_utility_room : bool, optional
        Whether the premises group is a utility room group. Default is False.
        Utility rooms apply an auxiliary premises impact correction coefficient
        (C_AUX = 0.3) per Section 138.
    is_residential_premises : bool, optional
        Whether the premises group is a residential premises group. Default is False.
        Affects amenities impact correction coefficient calculation.
    is_non_residential_premises : bool, optional
        Whether the premises group is a non-residential premises group. Default is False.
        Affects amenities impact correction coefficient calculation.
    floor : int, optional
        The highest floor number to which the premises is attached. Default is 2.
        Values < 1 indicate basement level. Affects floor impact correction coefficient:
        - Floor 1 for residential: K_st = 0.9 (Section 142.1)
        - Floor < 1 for residential: K_st = 0.6 (Section 142.2)
        - Other cases: K_st = 1.0 (Section 142.3)
    is_sewer : bool, optional
        Whether the premises has sewerage system. Default is True.
        Affects amenities impact correction coefficient for residential premises.
    is_sanitary_unit : bool, optional
        Whether the premises has a sanitary unit. Default is True.
        Affects amenities impact correction coefficient for residential premises.
    is_heating : bool, optional
        Whether the premises has heating system. Default is True.
        Affects amenities impact correction coefficient for both residential
        and non-residential premises.
    base_value : float, optional
        Override for the base premises group value (EUR per m²). Default is None.
        If provided, this value is used directly instead of looking up
        the base value via premises_group_base_value(usage_type, value_zone).

    Returns
    -------
    Optional[float]
        The calculated cadastral value in euros, rounded to 2 decimal places.
        Returns None if the calculation cannot be completed.
        
    Examples
    --------
    >>> group_premises_fiscal_cadastral_value_city('UT1110', '3-0010000-010', 1000, 100)
    727799.4
    
    >>> group_premises_fiscal_cadastral_value_city('UT1121', '3-0010000-030', 500)
    160075.0
    
    >>> # Residential premises on first floor without heating
    >>> group_premises_fiscal_cadastral_value_city(
    ...     usage_type='UT1110',
    ...     value_zone='3-0010000-010',
    ...     premises_area=75,
    ...     outdoor_area=10,
    ...     is_residential_premises=True,
    ...     floor=1,
    ...     is_heating=False
    ... )
    43104.51
    
    >>> # Utility room in basement
    >>> group_premises_fiscal_cadastral_value_city(
    ...     usage_type='UT1121',
    ...     value_zone='3-0010000-030',
    ...     premises_area=20,
    ...     is_utility_room=True,
    ...     floor=0
    ... )
    1920.9
    
    See Also
    --------
    premises_group_base_value : Function to retrieve base premises values by usage type and zone
    land_fiscal_cadastral_value_city : Function to calculate cadastral value for land in cities
    """
    C = 1 # vērtību attiecības koeficients
    C_OUTDOOR = 0.3 # ārtelpu platības korekcijas koeficients
    C_AUX = 0.3

    # daudzdzīvokļu mājas bāzes vērtība euro par kvadrātmetru;
    if base_value is not None:
        TG_bv = base_value
    else:
        TG_bv = premises_group_base_value(usage_type, value_zone)

    # telpu grupas kopējā vai par ārtelpām koriģētā platība    
    if outdoor_area > 0:
        A = round((premises_area - outdoor_area) + C_OUTDOOR * outdoor_area, 2)
    else:
        A = premises_area

    # apjoma ietekmes korekcijas koeficients;
    K_kor = 1

    # palīgtelpu ietekmes korekcijas koeficients
    if is_utility_room:
        K_p =  C_AUX
    else:
        K_p = 1

    # labiekārtojuma ietekmes korekcijas koeficients
    if is_residential_premises and not is_sewer and not is_sanitary_unit:
        K_lab = 0.6
    elif is_residential_premises and not is_sewer or not is_sanitary_unit:
        K_lab = 0.8
    elif is_residential_premises and is_sewer and is_sanitary_unit and not is_heating:
        K_lab = 0.9
    elif is_residential_premises:
        K_lab = 1
    elif is_non_residential_premises and not is_heating:
        K_lab = 0.9
    elif is_non_residential_premises:
        K_lab = 1
    else:
        K_lab = 1
         

    # stāva ietekmes korekcijas koeficients
    if is_residential_premises and floor == 1:
        K_st = 0.9
    elif is_residential_premises and floor < 1:
        K_st = 0.6
    else:
        K_st = 1

    # būves nolietojuma korekcijas koeficients
    K_s = 1

    # būves apgrūtinājumu korekcijas koeficients
    K_li = 1

    # ārsienu materiāla ietekmes korekcijas koeficients;
    K_am = 1

    # būvniecības perioda korekcijas koeficients
    K_bp = 1

    # 136. Telpu grupas kadastrālo vērtību aprēķina, izmantojot šādu formulu:
    return round(TG_bv * A * K_kor * K_p * K_lab * K_st * K_s * K_li * K_am * K_bp * C, 2)

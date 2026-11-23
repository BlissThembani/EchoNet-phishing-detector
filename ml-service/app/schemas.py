"""Request/response models: the 23 features selected in the notebook."""
from pydantic import BaseModel, Field


class WebPageFeatures(BaseModel):
    length_url: int
    length_hostname: int
    ip: int = Field(ge=0, le=1)
    nb_dots: int
    nb_qm: int
    nb_eq: int
    nb_slash: int
    nb_www: int
    ratio_digits_url: float
    ratio_digits_host: float
    tld_in_subdomain: int = Field(ge=0, le=1)
    prefix_suffix: int = Field(ge=0, le=1)
    shortest_word_host: int
    longest_words_raw: int
    longest_word_path: int
    phish_hints: int
    nb_hyperlinks: int
    ratio_intHyperlinks: float
    empty_title: int = Field(ge=0, le=1)
    domain_in_title: int = Field(ge=0, le=1)
    domain_age: int
    google_index: int = Field(ge=0, le=1)
    page_rank: int


class Prediction(BaseModel):
    prediction: str
    phishing_probability: float

export type Document = {
    attributes?:  { [key: string]: boolean | number | string };
    description?: null | string;
    documents:    DocumentRelationship[];
    id:           string;
    items?:       Item[];
    labels:       LabelRelationship[];
    title:        string;
    [property: string]: any;
}

export type DocumentRelationship = {
    timestamp?: Date | null;
    type:       string;
    value:      DocumentWithoutDocumentRelationships;
    [property: string]: any;
}

export type DocumentWithoutDocumentRelationships = {
    attributes?:  { [key: string]: boolean | number | string };
    description?: null | string;
    id:           string;
    items?:       Item[];
    labels?:      LabelRelationship[];
    title:        string;
    [property: string]: any;
}

export type Item = {
    content_type?: null | string;
    type:          string;
    url?:          null | string;
    [property: string]: any;
}

export type LabelRelationship = {
    timestamp?: Date | null;
    type:       string;
    value:      LabelWithoutLabelRelationships;
    [property: string]: any;
}

export type LabelWithoutLabelRelationships = {
    attributes?: { [key: string]: boolean | number | string };
    id:          string;
    type:        string;
    value:       string;
    [property: string]: any;
}

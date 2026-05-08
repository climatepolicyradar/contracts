/**
 * A document in the Climate Policy Radar corpus.
 */
export type Document = {
    /**
     * Full text content of the document
     */
    content?: null | string;
    /**
     * Unique identifier for the document
     */
    id: string;
    /**
     * Labels applied to this document
     */
    labels?: Label[];
    /**
     * Arbitrary additional metadata
     */
    metadata?: { [key: string]: any };
    /**
     * Date the document was published
     */
    publication_date?: Date | null;
    /**
     * URL of the source document
     */
    source_url?: null | string;
    /**
     * Document title
     */
    title: string;
    [property: string]: any;
}

/**
 * A classification label that can be applied to a Document.
 */
export type Label = {
    /**
     * Unique identifier for the label
     */
    id: string;
    /**
     * Human-readable label name
     */
    name: string;
    /**
     * Label category, e.g. 'sector', 'geography', 'instrument'
     */
    type: string;
    [property: string]: any;
}

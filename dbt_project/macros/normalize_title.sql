{#
    Normalize a title for fuzzy matching / deduplication:
      - lowercase
      - drop parenthetical / bracketed content:  "(feat. X)", "[Live]"
      - drop trailing " - suffix":               "- Remastered 2011", "- Live"
      - drop punctuation
      - collapse whitespace and trim
    e.g. "Lover Man (Oh, Where Can You Be?) - Live" -> "lover man"
#}
{% macro normalize_title(column) %}
    trim(
        regexp_replace(
            regexp_replace(
                regexp_replace(
                    regexp_replace(
                        lower({{ column }}),
                        '[\(\[][^\)\]]*[\)\]]', '', 'g'
                    ),
                    '\s+-\s+.*$', '', 'g'
                ),
                '[^a-z0-9 ]', '', 'g'
            ),
            '\s+', ' ', 'g'
        )
    )
{% endmacro %}

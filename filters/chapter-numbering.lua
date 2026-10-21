-- Introduce los niveles estructurales que el bloque de título ya muestra.
function Pandoc(doc)
  local prefix = doc.meta["mgp-number-prefix"]
  if not quarto.doc.is_format("html") or not prefix then return nil end
  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level == 1 then return nil end
  end
  -- Una cadena conserva componentes repetidos (por ejemplo, 16.1.1)
  -- durante la combinación de metadatos de Quarto.
  local depth = 0
  for _ in pandoc.utils.stringify(prefix):gmatch("%d+") do depth = depth + 1 end
  -- Las páginas de sección escriben ## para su primer nivel interior.
  if depth > 1 then
    doc = doc:walk({Header = function(header)
      header.level = math.min(6, header.level + depth - 1)
      return header
    end})
  end
  local headings = pandoc.List()
  for level = 1, depth do
    headings:insert(pandoc.Header(level, doc.meta.title,
      pandoc.Attr("mgp-chapter-" .. level, {"unlisted"})))
  end
  doc.blocks:insert(1, pandoc.Div(headings,
    pandoc.Attr("", {"mgp-chapter-anchor"}, {["aria-hidden"] = "true"})))
  return doc
end

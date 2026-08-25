-- Genera el armazón común de las preguntas PAES desde metadatos.
local function text(meta, key)
  if meta[key] == nil then return nil end
  return pandoc.utils.stringify(meta[key])
end

function Pandoc(doc)
  local number = text(doc.meta, "paes-question")
  if number == nil or number == "" then return nil end
  local tag, label = text(doc.meta, "knowledge-tag"), text(doc.meta, "paes-label")
  if tag == nil or label == nil then error("Una pregunta PAES requiere knowledge-tag y paes-label") end
  local title = "Pregunta " .. number .. " · " .. label
  local content = {pandoc.Header(2, "Pregunta " .. number)}
  for _, block in ipairs(doc.blocks) do table.insert(content, block) end
  doc.blocks = {pandoc.Div(content, pandoc.Attr("tag-" .. tag, {"knowledge-object"}, {
    tag = tag, type = "pregunta", title = title
  }))}
  return doc
end

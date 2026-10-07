-- El objeto aporta identidad; cada entorno matemático aporta su estilo.
local styles = {
  thm = "plain", prp = "plain", lem = "plain", cor = "plain",
  cnj = "plain", axm = "plain", law = "plain", principle = "plain",
  def = "definition", exm = "remark", rem = "remark"
}

function Div(div)
  local prefix = div.identifier:match("^([a-z]+)%-")
  local style = styles[prefix]
  if style then
    local class = "theorem-style-" .. style
    if not div.classes:includes(class) then div.classes:insert(class) end
    return div
  end

  if not div.classes:includes("knowledge-object") then return nil end
  local tag = div.attributes["tag"]
  if not tag then return nil end
  if quarto.doc.is_format("html") then return div end
  div.content:insert(1, pandoc.Para({
    pandoc.Span({pandoc.Str(tag)}, pandoc.Attr("", {"knowledge-tag"}))
  }))
  return div
end

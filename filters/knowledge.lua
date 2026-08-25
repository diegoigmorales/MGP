function Div(div)
  if not div.classes:includes("knowledge-object") then return nil end
  local tag = div.attributes["tag"]
  if not tag then return nil end

  div.content:insert(1, pandoc.Para({
    pandoc.Span({pandoc.Str("TAG " .. tag)}, pandoc.Attr("", {"knowledge-tag"}))
  }))

  return div
end

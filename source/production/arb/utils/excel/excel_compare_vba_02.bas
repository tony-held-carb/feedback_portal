' excel_compare_vba_02.bas
' VBA port of excel_compare.py, mimicking structure, naming, and output style.
' Batch mode: no MsgBox/InputBox, all output to timestamped .txt file.
' Divergences from Python are documented inline.

Option Explicit

' === CONFIGURATION ===
' Set your file/folder paths here (no user prompts)
Const FILE_A_PATH As String = "D:\local\cursor\feedback_portal\diagnostics\dairy_digester_operator_feedback_v006_for_review_local.xlsx"
Const FILE_B_PATH As String = "D:\local\cursor\feedback_portal\diagnostics\dairy_digester_operator_feedback_v006_for_review_sharepoint.xlsx"
Const DIR_A_PATH As String = "C:\Path\To\FolderA"
Const DIR_B_PATH As String = "C:\Path\To\FolderB"
Const OUTPUT_DIR As String = "D:\local\cursor\feedback_portal\diagnostics" ' Where to save diagnostic files

' === MAIN ENTRY POINT ===
Sub main()
    ' Entry point, analogous to if __name__ == "__main__": in Python
    ' Set up file paths and call compare_excel_files or compare_excel_directories
    Dim compare_dirs As Boolean: compare_dirs = False ' Set True to compare directories
    Dim formatting_mode As String: formatting_mode = "full" ' Options: off, common, full
    If compare_dirs Then
        compare_excel_directories DIR_A_PATH, DIR_B_PATH, formatting_mode
    Else
        compare_excel_files FILE_A_PATH, FILE_B_PATH, formatting_mode
    End If
End Sub

' === FILE COMPARISON ===
Sub compare_excel_files(file_a As String, file_b As String, Optional formatting_mode As String = "full")
    ' Mimics compare_excel_files in Python
    ' Calls compare_excel_content, writes output to timestamped .txt file
    Dim output As Collection: Set output = New Collection
    output.Add "Comparing:" & vbCrLf & "  A: " & file_a & vbCrLf & "  B: " & file_b & vbCrLf

    ' Hashing: VBA does not have built-in SHA-256; log file size and last modified as a proxy
    output.Add "File Info:"
    output.Add "  A: Size=" & get_file_size(file_a) & ", Modified=" & get_file_modified(file_a)
    output.Add "  B: Size=" & get_file_size(file_b) & ", Modified=" & get_file_modified(file_b)

    ' Open workbooks (read-only)
    Dim wbA As Workbook, wbB As Workbook
    Set wbA = Workbooks.Open(file_a, ReadOnly:=True)
    Set wbB = Workbooks.Open(file_b, ReadOnly:=True)

    ' Workbook-level and metadata comparisons
    compare_workbook_protection wbA, wbB, output
    compare_built_in_properties wbA, wbB, output
    compare_custom_properties wbA, wbB, output
    compare_defined_names wbA, wbB, output
    compare_theme wbA, wbB, output
    compare_vba_project wbA, wbB, output
    compare_external_links wbA, wbB, output
    compare_connections wbA, wbB, output

    compare_excel_content wbA, wbB, output, formatting_mode

    wbA.Close SaveChanges:=False
    wbB.Close SaveChanges:=False

    write_output_to_file output, "comparison"
End Sub

' === DIRECTORY COMPARISON ===
Sub compare_excel_directories(dir_a As String, dir_b As String, Optional formatting_mode As String = "common")
    ' Mimics compare_excel_directories in Python
    Dim fso As Object: Set fso = CreateObject("Scripting.FileSystemObject")
    Dim filesA As Object, filesB As Object
    Set filesA = fso.GetFolder(dir_a).Files
    Set filesB = fso.GetFolder(dir_b).Files
    Dim dictA As Object, dictB As Object
    Set dictA = CreateObject("Scripting.Dictionary")
    Set dictB = CreateObject("Scripting.Dictionary")
    Dim fileName As Variant
    Dim output As Collection: Set output = New Collection
    Dim in_both As Collection: Set in_both = New Collection
    Dim only_in_a As Collection: Set only_in_a = New Collection
    Dim only_in_b As Collection: Set only_in_b = New Collection

    ' Build dictionaries of .xlsx files
    For Each fileName In filesA
        If LCase(fso.GetExtensionName(fileName.Name)) = "xlsx" Then
            dictA(fileName.Name) = fileName.Path
        End If
    Next
    For Each fileName In filesB
        If LCase(fso.GetExtensionName(fileName.Name)) = "xlsx" Then
            dictB(fileName.Name) = fileName.Path
        End If
    Next

    ' Find only in A, only in B, in both
    For Each fileName In dictA.Keys
        If dictB.Exists(fileName) Then
            in_both.Add fileName
        Else
            only_in_a.Add fileName
        End If
    Next
    For Each fileName In dictB.Keys
        If Not dictA.Exists(fileName) Then
            only_in_b.Add fileName
        End If
    Next

    output.Add "Comparing Excel files in:" & vbCrLf & "  A: " & dir_a & vbCrLf & "  B: " & dir_b & vbCrLf
    output.Add "Files only in A (" & only_in_a.Count & "):"
    For Each fileName In only_in_a
        output.Add "  " & fileName
    Next
    output.Add "Files only in B (" & only_in_b.Count & "):"
    For Each fileName In only_in_b
        output.Add "  " & fileName
    Next
    output.Add "Files in both (" & in_both.Count & "):"
    For Each fileName In in_both
        output.Add vbCrLf & "=== Comparing " & fileName & " ==="
        compare_excel_files dictA(fileName), dictB(fileName), formatting_mode
        output.Add "(See separate comparison file for details)"
    Next
    write_output_to_file output, "directory_comparison"
End Sub

' === CONTENT COMPARISON ===
Sub compare_excel_content(wbA As Workbook, wbB As Workbook, output As Collection, formatting_mode As String)
    ' Mimics compare_excel_content in Python
    ' Divergence: VBA does not support set operations; uses dictionaries/collections
    Dim dictA As Object, dictB As Object
    Set dictA = CreateObject("Scripting.Dictionary")
    Set dictB = CreateObject("Scripting.Dictionary")
    Dim shName As Variant
    Dim only_in_a As Collection: Set only_in_a = New Collection
    Dim only_in_b As Collection: Set only_in_b = New Collection
    Dim in_both As Collection: Set in_both = New Collection

    ' Build dictionaries of sheet names
    For Each shName In wbA.Sheets
        dictA(shName.Name) = True
    Next
    For Each shName In wbB.Sheets
        dictB(shName.Name) = True
    Next
    For Each shName In dictA.Keys
        If dictB.Exists(shName) Then
            in_both.Add shName
        Else
            only_in_a.Add shName
        End If
    Next
    For Each shName In dictB.Keys
        If Not dictA.Exists(shName) Then
            only_in_b.Add shName
        End If
    Next

    If only_in_a.Count > 0 Then
        output.Add "[Sheets only in A]"
        For Each shName In only_in_a
            output.Add "  " & shName
        Next
    End If
    If only_in_b.Count > 0 Then
        output.Add "[Sheets only in B]"
        For Each shName In only_in_b
            output.Add "  " & shName
        Next
    End If

    Dim sheet As Variant
    For Each sheet In in_both
        output.Add vbCrLf & "=== Sheet: " & sheet & " ==="
        compare_sheet_content wbA.Sheets(sheet), wbB.Sheets(sheet), output, formatting_mode
    Next
End Sub

' === SHEET CONTENT COMPARISON ===
Sub compare_sheet_content(wsA As Worksheet, wsB As Worksheet, output As Collection, formatting_mode As String)
    ' Comprehensive: Compare all possible cell-level differences, with formatting_mode (off, common, full)
    Dim maxRow As Long, maxCol As Long
    maxRow = Application.WorksheetFunction.Max(wsA.UsedRange.Rows.Count, wsB.UsedRange.Rows.Count)
    maxCol = Application.WorksheetFunction.Max(wsA.UsedRange.Columns.Count, wsB.UsedRange.Columns.Count)
    Dim r As Long, c As Long
    Dim cellA As Range, cellB As Range
    Dim coord As String
    Dim foundDiff As Boolean: foundDiff = False
    Dim diffType As String
    
    output.Add "[Content Differences]"
    For r = 1 To maxRow
        For c = 1 To maxCol
            Set cellA = wsA.Cells(r, c)
            Set cellB = wsB.Cells(r, c)
            coord = cellA.Address(False, False)
            ' Value
            If safe_val(cellA.Value) <> safe_val(cellB.Value) Then
                output.Add "  " & coord & ": Value differs\n    A: " & safe_val(cellA.Value) & "\n    B: " & safe_val(cellB.Value)
                foundDiff = True
            End If
            ' Formula
            If safe_val(cellA.HasFormula, False) Or safe_val(cellB.HasFormula, False) Then
                If safe_val(cellA.Formula) <> safe_val(cellB.Formula) Then
                    output.Add "  " & coord & ": Formula differs\n    A: " & safe_val(cellA.Formula) & "\n    B: " & safe_val(cellB.Formula)
                    foundDiff = True
                End If
            End If
            ' Comment
            Dim commA As String, commB As String
            commA = "": commB = ""
            If Not cellA.Comment Is Nothing Then commA = safe_val(cellA.Comment.Text)
            If Not cellB.Comment Is Nothing Then commB = safe_val(cellB.Comment.Text)
            If commA <> commB Then
                output.Add "  " & coord & ": Comment differs\n    A: " & commA & "\n    B: " & commB
                foundDiff = True
            End If
            ' Data validation (dropdowns)
            If has_validation(cellA) Or has_validation(cellB) Then
                Dim valA As String, valB As String
                valA = get_validation_formula(cellA)
                valB = get_validation_formula(cellB)
                If valA <> valB Then
                    output.Add "  " & coord & ": Data validation differs\n    A: " & valA & "\n    B: " & valB
                    foundDiff = True
                End If
            End If
            ' Protection
            If safe_val(cellA.Locked, False) <> safe_val(cellB.Locked, False) Or safe_val(cellA.FormulaHidden, False) <> safe_val(cellB.FormulaHidden, False) Then
                output.Add "  " & coord & ": Protection differs\n    A: Locked=" & safe_val(cellA.Locked, False) & ", Hidden=" & safe_val(cellA.FormulaHidden, False) & "\n    B: Locked=" & safe_val(cellB.Locked, False) & ", Hidden=" & safe_val(cellB.FormulaHidden, False)
                foundDiff = True
            End If
            ' Formatting checks by mode
            If formatting_mode = "common" Or formatting_mode = "full" Then
                foundDiff = compare_and_log_font(cellA.Font, cellB.Font, coord, output, formatting_mode) Or foundDiff
                foundDiff = compare_and_log_fill(cellA.Interior, cellB.Interior, coord, output, formatting_mode) Or foundDiff
                If safe_val(cellA.NumberFormat) <> safe_val(cellB.NumberFormat) Then
                    output.Add "  " & coord & ": NumberFormat differs\n    A: " & safe_val(cellA.NumberFormat) & "\n    B: " & safe_val(cellB.NumberFormat)
                    foundDiff = True
                End If
                foundDiff = compare_and_log_alignment(cellA, cellB, coord, output, formatting_mode) Or foundDiff
            End If
            If formatting_mode = "full" Then
                foundDiff = compare_and_log_borders(cellA.Borders, cellB.Borders, coord, output) Or foundDiff
            End If
        Next c
    Next r
    ' Row/column hidden status, height/width
    output.Add "[Row/Column Differences]"
    For r = 1 To maxRow
        If safe_val(wsA.Rows(r).Hidden, False) <> safe_val(wsB.Rows(r).Hidden, False) Then
            output.Add "  Row " & r & ": Hidden differs\n    A: " & safe_val(wsA.Rows(r).Hidden, False) & "\n    B: " & safe_val(wsB.Rows(r).Hidden, False)
            foundDiff = True
        End If
        If safe_val(wsA.Rows(r).RowHeight, 0) <> safe_val(wsB.Rows(r).RowHeight, 0) Then
            output.Add "  Row " & r & ": RowHeight differs\n    A: " & safe_val(wsA.Rows(r).RowHeight, 0) & "\n    B: " & safe_val(wsB.Rows(r).RowHeight, 0)
            foundDiff = True
        End If
    Next r
    For c = 1 To maxCol
        If safe_val(wsA.Columns(c).Hidden, False) <> safe_val(wsB.Columns(c).Hidden, False) Then
            output.Add "  Column " & c & ": Hidden differs\n    A: " & safe_val(wsA.Columns(c).Hidden, False) & "\n    B: " & safe_val(wsB.Columns(c).Hidden, False)
            foundDiff = True
        End If
        If safe_val(wsA.Columns(c).ColumnWidth, 0) <> safe_val(wsB.Columns(c).ColumnWidth, 0) Then
            output.Add "  Column " & c & ": ColumnWidth differs\n    A: " & safe_val(wsA.Columns(c).ColumnWidth, 0) & "\n    B: " & safe_val(wsB.Columns(c).ColumnWidth, 0)
            foundDiff = True
        End If
    Next c
    ' Sheet protection
    output.Add "[Sheet Protection Differences]"
    If Not compare_sheet_protection(wsA, wsB, output) Then
        output.Add "  No sheet protection differences."
    Else
        foundDiff = True
    End If
    If Not foundDiff Then
        output.Add "  No differences found."
    End If
End Sub

' === SAFE VALUE HELPER ===
Function safe_val(val As Variant, Optional defaultVal As Variant = "") As Variant
    If IsNull(val) Or IsEmpty(val) Then
        safe_val = defaultVal
    Else
        safe_val = val
    End If
End Function

' === FONT COMPARISON ===
Function compare_font(f1 As Font, f2 As Font) As Boolean
    compare_font = (safe_val(f1.Name) = safe_val(f2.Name)) And _
                   (safe_val(f1.Size, 0) = safe_val(f2.Size, 0)) And _
                   (safe_val(f1.Bold, False) = safe_val(f2.Bold, False)) And _
                   (safe_val(f1.Italic, False) = safe_val(f2.Italic, False)) And _
                   (safe_val(f1.Underline, False) = safe_val(f2.Underline, False)) And _
                   (safe_val(f1.Color, 0) = safe_val(f2.Color, 0)) And _
                   (safe_val(f1.Strikethrough, False) = safe_val(f2.Strikethrough, False)) And _
                   (safe_val(f1.Superscript, False) = safe_val(f2.Superscript, False)) And _
                   (safe_val(f1.Subscript, False) = safe_val(f2.Subscript, False))
End Function

Function font_to_string(f As Font) As String
    font_to_string = "Name:" & safe_val(f.Name) & ", Size:" & safe_val(f.Size, 0) & _
        ", Bold:" & safe_val(f.Bold, False) & ", Italic:" & safe_val(f.Italic, False) & _
        ", Underline:" & safe_val(f.Underline, False) & ", Color:" & safe_val(f.Color, 0) & _
        ", Strike:" & safe_val(f.Strikethrough, False) & ", Super:" & safe_val(f.Superscript, False) & _
        ", Sub:" & safe_val(f.Subscript, False)
End Function

' === ALIGNMENT COMPARISON ===
Function compare_alignment(cellA As Range, cellB As Range) As Boolean
    compare_alignment = (safe_val(cellA.HorizontalAlignment) = safe_val(cellB.HorizontalAlignment)) And _
                       (safe_val(cellA.VerticalAlignment) = safe_val(cellB.VerticalAlignment)) And _
                       (safe_val(cellA.WrapText, False) = safe_val(cellB.WrapText, False)) And _
                       (safe_val(cellA.Orientation, 0) = safe_val(cellB.Orientation, 0)) And _
                       (safe_val(cellA.ShrinkToFit, False) = safe_val(cellB.ShrinkToFit, False)) And _
                       (safe_val(cellA.IndentLevel, 0) = safe_val(cellB.IndentLevel, 0))
End Function

Function alignment_to_string(cell As Range) As String
    alignment_to_string = "H:" & safe_val(cell.HorizontalAlignment) & ", V:" & safe_val(cell.VerticalAlignment) & _
        ", Wrap:" & safe_val(cell.WrapText, False) & ", Orient:" & safe_val(cell.Orientation, 0) & _
        ", Shrink:" & safe_val(cell.ShrinkToFit, False) & ", Indent:" & safe_val(cell.IndentLevel, 0)
End Function

' === BORDER COMPARISON ===
Function compare_borders(b1 As Borders, b2 As Borders) As Boolean
    compare_borders = True
    Dim side As Variant
    For Each side In Array(xlEdgeLeft, xlEdgeRight, xlEdgeTop, xlEdgeBottom)
        If safe_val(b1(side).LineStyle) <> safe_val(b2(side).LineStyle) Or _
           safe_val(b1(side).Color, 0) <> safe_val(b2(side).Color, 0) Or _
           safe_val(b1(side).Weight, 0) <> safe_val(b2(side).Weight, 0) Then
            compare_borders = False
            Exit Function
        End If
    Next
End Function

' === DATA VALIDATION HELPERS ===
Function has_validation(cell As Range) As Boolean
    On Error Resume Next
    has_validation = Not cell.Validation Is Nothing
    On Error GoTo 0
End Function

Function get_validation_formula(cell As Range) As String
    On Error Resume Next
    If Not cell.Validation Is Nothing Then
        get_validation_formula = cell.Validation.Formula1
    Else
        get_validation_formula = ""
    End If
    On Error GoTo 0
End Function

' === SHEET PROTECTION COMPARISON ===
Function compare_sheet_protection(wsA As Worksheet, wsB As Worksheet, output As Collection) As Boolean
    ' Returns True if differences found
    Dim found As Boolean: found = False
    If wsA.ProtectContents <> wsB.ProtectContents Then
        output.Add "  ProtectContents differs\n    A: " & wsA.ProtectContents & "\n    B: " & wsB.ProtectContents
        found = True
    End If
    If wsA.ProtectDrawingObjects <> wsB.ProtectDrawingObjects Then
        output.Add "  ProtectDrawingObjects differs\n    A: " & wsA.ProtectDrawingObjects & "\n    B: " & wsB.ProtectDrawingObjects
        found = True
    End If
    If wsA.ProtectScenarios <> wsB.ProtectScenarios Then
        output.Add "  ProtectScenarios differs\n    A: " & wsA.ProtectScenarios & "\n    B: " & wsB.ProtectScenarios
        found = True
    End If
    compare_sheet_protection = found
End Function

' === FONT DETAIL COMPARISON ===
Function compare_and_log_font(f1 As Font, f2 As Font, coord As String, output As Collection, formatting_mode As String) As Boolean
    Dim found As Boolean: found = False
    Dim props As Variant, p As Variant
    If formatting_mode = "full" Then
        props = Array("Name", "Size", "Bold", "Italic", "Underline", "Color", "Strikethrough", "Superscript", "Subscript", "ThemeColor", "TintAndShade")
    Else
        props = Array("Name", "Size", "Bold", "Italic", "Underline", "Color")
    End If
    For Each p In props
        Dim v1 As Variant, v2 As Variant
        On Error Resume Next
        Err.Clear
        v1 = CallByName(f1, p, VbGet)
        v2 = CallByName(f2, p, VbGet)
        If Err.Number = 0 Then
            If safe_val(v1) <> safe_val(v2) Then
                output.Add "  " & coord & ": Font." & p & " differs\n    A: " & safe_val(v1) & "\n    B: " & safe_val(v2)
                found = True
            End If
        End If
        On Error GoTo 0
    Next
    compare_and_log_font = found
End Function

' === FILL DETAIL COMPARISON ===
Function compare_and_log_fill(i1 As Interior, i2 As Interior, coord As String, output As Collection, formatting_mode As String) As Boolean
    Dim found As Boolean: found = False
    Dim props As Variant, p As Variant
    If formatting_mode = "full" Then
        props = Array("Color", "ColorIndex", "Pattern", "PatternColor", "PatternColorIndex", "ThemeColor", "TintAndShade")
    Else
        props = Array("Color", "Pattern")
    End If
    For Each p In props
        Dim v1 As Variant, v2 As Variant
        On Error Resume Next
        Err.Clear
        v1 = CallByName(i1, p, VbGet)
        v2 = CallByName(i2, p, VbGet)
        If Err.Number = 0 Then
            If safe_val(v1) <> safe_val(v2) Then
                output.Add "  " & coord & ": Fill." & p & " differs\n    A: " & safe_val(v1) & "\n    B: " & safe_val(v2)
                found = True
            End If
        End If
        On Error GoTo 0
    Next
    compare_and_log_fill = found
End Function

' === ALIGNMENT DETAIL COMPARISON ===
Function compare_and_log_alignment(cellA As Range, cellB As Range, coord As String, output As Collection, formatting_mode As String) As Boolean
    Dim found As Boolean: found = False
    Dim props As Variant, p As Variant
    If formatting_mode = "full" Then
        props = Array("HorizontalAlignment", "VerticalAlignment", "WrapText", "Orientation", "ShrinkToFit", "IndentLevel", "ReadingOrder")
    Else
        props = Array("HorizontalAlignment", "VerticalAlignment", "WrapText")
    End If
    For Each p In props
        Dim v1 As Variant, v2 As Variant
        On Error Resume Next
        Err.Clear
        v1 = CallByName(cellA, p, VbGet)
        v2 = CallByName(cellB, p, VbGet)
        If Err.Number = 0 Then
            If safe_val(v1) <> safe_val(v2) Then
                output.Add "  " & coord & ": Alignment." & p & " differs\n    A: " & safe_val(v1) & "\n    B: " & safe_val(v2)
                found = True
            End If
        End If
        On Error GoTo 0
    Next
    compare_and_log_alignment = found
End Function

' === BORDER DETAIL COMPARISON ===
Function compare_and_log_borders(b1 As Borders, b2 As Borders, coord As String, output As Collection) As Boolean
    Dim found As Boolean: found = False
    Dim sides As Variant, props As Variant, s As Variant, p As Variant
    sides = Array(xlEdgeLeft, xlEdgeRight, xlEdgeTop, xlEdgeBottom, xlInsideHorizontal, xlInsideVertical)
    props = Array("LineStyle", "Color", "ColorIndex", "ThemeColor", "TintAndShade", "Weight")
    For Each s In sides
        For Each p In props
            Dim v1 As Variant, v2 As Variant
            On Error Resume Next
            Err.Clear
            v1 = CallByName(b1(s), p, VbGet)
            v2 = CallByName(b2(s), p, VbGet)
            If Err.Number = 0 Then
                If safe_val(v1) <> safe_val(v2) Then
                    output.Add "  " & coord & ": Border(" & s & ")." & p & " differs\n    A: " & safe_val(v1) & "\n    B: " & safe_val(v2)
                    found = True
                End If
            End If
            On Error GoTo 0
        Next
    Next
    compare_and_log_borders = found
End Function

' === WORKBOOK-LEVEL PROTECTION ===
Sub compare_workbook_protection(wbA As Workbook, wbB As Workbook, output As Collection)
    If safe_val(wbA.ProtectStructure, False) <> safe_val(wbB.ProtectStructure, False) Then
        output.Add "[Workbook Protection] Structure differs" & vbCrLf & _
                   "    A: " & safe_val(wbA.ProtectStructure, False) & vbCrLf & _
                   "    B: " & safe_val(wbB.ProtectStructure, False)
    End If
    If safe_val(wbA.ProtectWindows, False) <> safe_val(wbB.ProtectWindows, False) Then
        output.Add "[Workbook Protection] Windows differs" & vbCrLf & _
                   "    A: " & safe_val(wbA.ProtectWindows, False) & vbCrLf & _
                   "    B: " & safe_val(wbB.ProtectWindows, False)
    End If
    If safe_val(wbA.Password, "") <> safe_val(wbB.Password, "") Then
        output.Add "[Workbook Protection] Password presence differs"
    End If
End Sub

' === BUILT-IN DOCUMENT PROPERTIES ===
Sub compare_built_in_properties(wbA As Workbook, wbB As Workbook, output As Collection)
    Dim prop As Variant
    For Each prop In wbA.BuiltinDocumentProperties
        On Error Resume Next
        Dim valA As Variant, valB As Variant
        valA = safe_val(wbA.BuiltinDocumentProperties(prop.Name))
        valB = safe_val(wbB.BuiltinDocumentProperties(prop.Name))
        If valA <> valB Then
            output.Add "[Workbook Property] " & prop.Name & " differs" & vbCrLf & _
                       "    A: " & valA & vbCrLf & "    B: " & valB
        End If
        On Error GoTo 0
    Next
End Sub

' === CUSTOM DOCUMENT PROPERTIES ===
Sub compare_custom_properties(wbA As Workbook, wbB As Workbook, output As Collection)
    Dim prop As Variant
    For Each prop In wbA.CustomDocumentProperties
        On Error Resume Next
        Dim valA As Variant, valB As Variant
        valA = safe_val(wbA.CustomDocumentProperties(prop.Name))
        valB = safe_val(wbB.CustomDocumentProperties(prop.Name))
        If valA <> valB Then
            output.Add "[Custom Property] " & prop.Name & " differs" & vbCrLf & _
                       "    A: " & valA & vbCrLf & "    B: " & valB
        End If
        On Error GoTo 0
    Next
End Sub

' === DEFINED NAMES ===
Sub compare_defined_names(wbA As Workbook, wbB As Workbook, output As Collection)
    Dim nA As Name, nB As Name
    For Each nA In wbA.Names
        Set nB = Nothing
        On Error Resume Next
        Set nB = wbB.Names(nA.Name)
        On Error GoTo 0
        If nB Is Nothing Then
            output.Add "[Defined Name] " & nA.Name & " only in A"
        ElseIf nA.RefersTo <> nB.RefersTo Then
            output.Add "[Defined Name] " & nA.Name & " refers to different ranges" & vbCrLf & _
                       "    A: " & nA.RefersTo & vbCrLf & "    B: " & nB.RefersTo
        End If
    Next
    For Each nB In wbB.Names
        On Error Resume Next
        Set nA = wbA.Names(nB.Name)
        On Error GoTo 0
        If nA Is Nothing Then
            output.Add "[Defined Name] " & nB.Name & " only in B"
        End If
    Next
End Sub

' === THEME COMPARISON ===
Sub compare_theme(wbA As Workbook, wbB As Workbook, output As Collection)
    On Error Resume Next
    Dim themeA As Variant, themeB As Variant
    themeA = wbA.Theme.ThemeColorScheme
    themeB = wbB.Theme.ThemeColorScheme
    If themeA <> themeB Then
        output.Add "[Workbook Theme] ThemeColorScheme differs" & vbCrLf & _
                   "    A: " & themeA & vbCrLf & "    B: " & themeB
    End If
    On Error GoTo 0
End Sub

' === VBA PROJECT PRESENCE ===
Sub compare_vba_project(wbA As Workbook, wbB As Workbook, output As Collection)
    On Error Resume Next
    Dim hasVBA_A As Boolean, hasVBA_B As Boolean
    hasVBA_A = Not wbA.VBProject Is Nothing
    hasVBA_B = Not wbB.VBProject Is Nothing
    If hasVBA_A <> hasVBA_B Then
        output.Add "[VBA Project] Presence differs" & vbCrLf & _
                   "    A: " & hasVBA_A & vbCrLf & "    B: " & hasVBA_B
    End If
    On Error GoTo 0
End Sub

' === EXTERNAL LINKS ===
Sub compare_external_links(wbA As Workbook, wbB As Workbook, output As Collection)
    On Error Resume Next
    Dim linksA As Variant, linksB As Variant
    linksA = wbA.LinkSources(xlLinkTypeExcelLinks)
    linksB = wbB.LinkSources(xlLinkTypeExcelLinks)
    If safe_val(linksA, "") <> safe_val(linksB, "") Then
        output.Add "[External Links] ExcelLinks differ" & vbCrLf & _
                   "    A: " & safe_val(linksA, "None") & vbCrLf & "    B: " & safe_val(linksB, "None")
    End If
    On Error GoTo 0
End Sub

' === CONNECTIONS ===
Sub compare_connections(wbA As Workbook, wbB As Workbook, output As Collection)
    On Error Resume Next
    Dim connA As WorkbookConnection, connB As WorkbookConnection
    Dim dictA As Object, dictB As Object
    Set dictA = CreateObject("Scripting.Dictionary")
    Set dictB = CreateObject("Scripting.Dictionary")
    For Each connA In wbA.Connections
        dictA(connA.Name) = connA.Description
    Next
    For Each connB In wbB.Connections
        dictB(connB.Name) = connB.Description
    Next
    Dim k As Variant
    For Each k In dictA.Keys
        If Not dictB.Exists(k) Then
            output.Add "[Connection] " & k & " only in A"
        ElseIf dictA(k) <> dictB(k) Then
            output.Add "[Connection] " & k & " description differs" & vbCrLf & _
                       "    A: " & dictA(k) & vbCrLf & "    B: " & dictB(k)
        End If
    Next
    For Each k In dictB.Keys
        If Not dictA.Exists(k) Then
            output.Add "[Connection] " & k & " only in B"
        End If
    Next
    On Error GoTo 0
End Sub

' === FILE OUTPUT ===
Sub write_output_to_file(output As Collection, prefix As String)
    ' Writes output to a timestamped .txt file in OUTPUT_DIR
    Dim nowStr As String
    nowStr = Format(Now, "yyyymmdd_hhnnss")
    Dim outPath As String
    outPath = OUTPUT_DIR & "\" & prefix & "_at_" & nowStr & ".txt"
    Dim fnum As Integer: fnum = FreeFile
    Open outPath For Output As #fnum
    Dim line As Variant
    For Each line In output
        Print #fnum, line
    Next
    Close #fnum
End Sub

' === FILE INFO HELPERS ===
Function get_file_size(path As String) As Long
    ' Returns file size in bytes
    Dim fso As Object: Set fso = CreateObject("Scripting.FileSystemObject")
    get_file_size = fso.GetFile(path).Size
End Function

Function get_file_modified(path As String) As String
    ' Returns file last modified date as string
    Dim fso As Object: Set fso = CreateObject("Scripting.FileSystemObject")
    get_file_modified = fso.GetFile(path).DateLastModified
End Function

' === NOTES ON DIVERGENCES ===
' - No SHA-256: VBA lacks built-in hash, so file size/date are used as a proxy.
' - No set operations: Uses dictionaries/collections for sheet/file tracking.
' - No batch directory compare output in one file: Each file-pair comparison gets its own file.
' - No MsgBox/InputBox: All output is written to file, no user interaction.
' - Formatting checks are basic; extend as needed for more fidelity.
' - Error handling is minimal; add as needed for robustness. 
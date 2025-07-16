'========================================
' ExcelCompareVBA Module
' Ported from excel_compare.py (Python)
' Compares two Excel workbooks for content, formatting, protection, and more.
' Outputs a summary of all differences to a new worksheet.
'========================================

Option Explicit

' Entry point for comparing two workbooks
Sub Test_CompareWorkbooks()
    Dim fileA As String, fileB As String
    fileA = "C:\Path\To\FileA.xlsx" ' <-- Set your file paths
    fileB = "C:\Path\To\FileB.xlsx"
    CompareWorkbooks fileA, fileB
End Sub

' Main comparison routine
Sub CompareWorkbooks(fileA As String, fileB As String)
    Dim wbA As Workbook, wbB As Workbook
    Dim diffWs As Worksheet
    Dim diffRow As Long
    Dim summary As String
    
    ' Open both workbooks (read-only)
    Set wbA = Workbooks.Open(fileA, ReadOnly:=True)
    Set wbB = Workbooks.Open(fileB, ReadOnly:=True)
    
    ' Create a new worksheet for differences
    Set diffWs = ThisWorkbook.Sheets.Add
    diffWs.Name = "Differences"
    diffWs.Cells(1, 1).Resize(1, 6).Value = Array("Sheet", "Cell", "Type", "FileA", "FileB", "Details")
    diffRow = 2
    
    ' Compare workbook protection
    summary = CompareWorkbookProtection(wbA, wbB, diffWs, diffRow)
    
    ' Compare sheets
    summary = summary & CompareSheets(wbA, wbB, diffWs, diffRow)
    
    ' Close the workbooks
    wbA.Close SaveChanges:=False
    wbB.Close SaveChanges:=False
    
    ' Autofit columns and show summary
    diffWs.Columns.AutoFit
    MsgBox "Comparison complete." & vbCrLf & summary, vbInformation
End Sub

' Compare workbook-level protection
Function CompareWorkbookProtection(wbA As Workbook, wbB As Workbook, diffWs As Worksheet, diffRow As Long) As String
    Dim summary As String
    summary = ""
    If wbA.ProtectStructure <> wbB.ProtectStructure Then
        diffWs.Cells(diffRow, 1).Value = "[Workbook Protection]"
        diffWs.Cells(diffRow, 3).Value = "ProtectStructure"
        diffWs.Cells(diffRow, 4).Value = wbA.ProtectStructure
        diffWs.Cells(diffRow, 5).Value = wbB.ProtectStructure
        diffRow = diffRow + 1
        summary = summary & "Workbook structure protection differs." & vbCrLf
    End If
    If wbA.ProtectWindows <> wbB.ProtectWindows Then
        diffWs.Cells(diffRow, 1).Value = "[Workbook Protection]"
        diffWs.Cells(diffRow, 3).Value = "ProtectWindows"
        diffWs.Cells(diffRow, 4).Value = wbA.ProtectWindows
        diffWs.Cells(diffRow, 5).Value = wbB.ProtectWindows
        diffRow = diffRow + 1
        summary = summary & "Workbook windows protection differs." & vbCrLf
    End If
    CompareWorkbookProtection = summary
End Function

' Compare sheets, their presence, and all content/formatting
Function CompareSheets(wbA As Workbook, wbB As Workbook, diffWs As Worksheet, diffRow As Long) As String
    Dim summary As String
    Dim dictA As Object, dictB As Object
    Dim shName As Variant
    Dim onlyInA As String, onlyInB As String
    Set dictA = CreateObject("Scripting.Dictionary")
    Set dictB = CreateObject("Scripting.Dictionary")
    summary = ""
    
    ' Build dictionaries of sheet names
    For Each shName In wbA.Sheets
        dictA(shName.Name) = True
    Next
    For Each shName In wbB.Sheets
        dictB(shName.Name) = True
    Next
    
    ' Sheets only in A
    onlyInA = ""
    For Each shName In dictA.Keys
        If Not dictB.Exists(shName) Then
            onlyInA = onlyInA & shName & ", "
            diffWs.Cells(diffRow, 1).Value = shName
            diffWs.Cells(diffRow, 3).Value = "Sheet only in FileA"
            diffRow = diffRow + 1
        End If
    Next
    If onlyInA <> "" Then summary = summary & "Sheets only in FileA: " & onlyInA & vbCrLf
    
    ' Sheets only in B
    onlyInB = ""
    For Each shName In dictB.Keys
        If Not dictA.Exists(shName) Then
            onlyInB = onlyInB & shName & ", "
            diffWs.Cells(diffRow, 1).Value = shName
            diffWs.Cells(diffRow, 3).Value = "Sheet only in FileB"
            diffRow = diffRow + 1
        End If
    Next
    If onlyInB <> "" Then summary = summary & "Sheets only in FileB: " & onlyInB & vbCrLf
    
    ' Sheets in both
    For Each shName In dictA.Keys
        If dictB.Exists(shName) Then
            summary = summary & CompareSheetContent(wbA.Sheets(shName), wbB.Sheets(shName), diffWs, diffRow)
        End If
    Next
    
    CompareSheets = summary
End Function

' Compare all content and formatting in a pair of sheets
Function CompareSheetContent(wsA As Worksheet, wsB As Worksheet, diffWs As Worksheet, diffRow As Long) As String
    Dim summary As String
    Dim maxRow As Long, maxCol As Long
    Dim r As Long, c As Long
    Dim cellA As Range, cellB As Range
    Dim coord As String
    
    summary = ""
    maxRow = Application.WorksheetFunction.Max(wsA.UsedRange.Rows.Count, wsB.UsedRange.Rows.Count)
    maxCol = Application.WorksheetFunction.Max(wsA.UsedRange.Columns.Count, wsB.UsedRange.Columns.Count)
    
    ' Compare sheet protection
    If wsA.ProtectContents <> wsB.ProtectContents Then
        diffWs.Cells(diffRow, 1).Value = wsA.Name
        diffWs.Cells(diffRow, 3).Value = "Sheet Protection"
        diffWs.Cells(diffRow, 4).Value = wsA.ProtectContents
        diffWs.Cells(diffRow, 5).Value = wsB.ProtectContents
        diffRow = diffRow + 1
        summary = summary & "Sheet protection differs in " & wsA.Name & vbCrLf
    End If
    
    ' Compare each cell
    For r = 1 To maxRow
        For c = 1 To maxCol
            Set cellA = wsA.Cells(r, c)
            Set cellB = wsB.Cells(r, c)
            coord = cellA.Address
            
            ' Value
            If cellA.Value <> cellB.Value Then
                diffWs.Cells(diffRow, 1).Value = wsA.Name
                diffWs.Cells(diffRow, 2).Value = coord
                diffWs.Cells(diffRow, 3).Value = "Value"
                diffWs.Cells(diffRow, 4).Value = cellA.Value
                diffWs.Cells(diffRow, 5).Value = cellB.Value
                diffRow = diffRow + 1
            End If
            
            ' Formula
            If cellA.HasFormula Or cellB.HasFormula Then
                If cellA.Formula <> cellB.Formula Then
                    diffWs.Cells(diffRow, 1).Value = wsA.Name
                    diffWs.Cells(diffRow, 2).Value = coord
                    diffWs.Cells(diffRow, 3).Value = "Formula"
                    diffWs.Cells(diffRow, 4).Value = cellA.Formula
                    diffWs.Cells(diffRow, 5).Value = cellB.Formula
                    diffRow = diffRow + 1
                End If
            End If
            
            ' Comment
            If Not cellA.Comment Is Nothing Or Not cellB.Comment Is Nothing Then
                Dim commA As String, commB As String
                commA = ""
                commB = ""
                If Not cellA.Comment Is Nothing Then commA = cellA.Comment.Text
                If Not cellB.Comment Is Nothing Then commB = cellB.Comment.Text
                If commA <> commB Then
                    diffWs.Cells(diffRow, 1).Value = wsA.Name
                    diffWs.Cells(diffRow, 2).Value = coord
                    diffWs.Cells(diffRow, 3).Value = "Comment"
                    diffWs.Cells(diffRow, 4).Value = commA
                    diffWs.Cells(diffRow, 5).Value = commB
                    diffRow = diffRow + 1
                End If
            End If
            
            ' Data validation (dropdowns)
            If HasValidation(cellA) Or HasValidation(cellB) Then
                Dim valA As String, valB As String
                valA = GetValidationFormula(cellA)
                valB = GetValidationFormula(cellB)
                If valA <> valB Then
                    diffWs.Cells(diffRow, 1).Value = wsA.Name
                    diffWs.Cells(diffRow, 2).Value = coord
                    diffWs.Cells(diffRow, 3).Value = "Validation"
                    diffWs.Cells(diffRow, 4).Value = valA
                    diffWs.Cells(diffRow, 5).Value = valB
                    diffRow = diffRow + 1
                End If
            End If
            
            ' Protection
            If cellA.Locked <> cellB.Locked Or cellA.FormulaHidden <> cellB.FormulaHidden Then
                diffWs.Cells(diffRow, 1).Value = wsA.Name
                diffWs.Cells(diffRow, 2).Value = coord
                diffWs.Cells(diffRow, 3).Value = "Protection"
                diffWs.Cells(diffRow, 4).Value = "Locked:" & cellA.Locked & ", Hidden:" & cellA.FormulaHidden
                diffWs.Cells(diffRow, 5).Value = "Locked:" & cellB.Locked & ", Hidden:" & cellB.FormulaHidden
                diffRow = diffRow + 1
            End If
            
            ' Formatting: Font
            If Not CompareFont(cellA.Font, cellB.Font) Then
                diffWs.Cells(diffRow, 1).Value = wsA.Name
                diffWs.Cells(diffRow, 2).Value = coord
                diffWs.Cells(diffRow, 3).Value = "Font"
                diffWs.Cells(diffRow, 4).Value = FontToString(cellA.Font)
                diffWs.Cells(diffRow, 5).Value = FontToString(cellB.Font)
                diffRow = diffRow + 1
            End If
            
            ' Formatting: Fill
            If cellA.Interior.Color <> cellB.Interior.Color Then
                diffWs.Cells(diffRow, 1).Value = wsA.Name
                diffWs.Cells(diffRow, 2).Value = coord
                diffWs.Cells(diffRow, 3).Value = "Fill"
                diffWs.Cells(diffRow, 4).Value = cellA.Interior.Color
                diffWs.Cells(diffRow, 5).Value = cellB.Interior.Color
                diffRow = diffRow + 1
            End If
            
            ' Formatting: NumberFormat
            If cellA.NumberFormat <> cellB.NumberFormat Then
                diffWs.Cells(diffRow, 1).Value = wsA.Name
                diffWs.Cells(diffRow, 2).Value = coord
                diffWs.Cells(diffRow, 3).Value = "NumberFormat"
                diffWs.Cells(diffRow, 4).Value = cellA.NumberFormat
                diffWs.Cells(diffRow, 5).Value = cellB.NumberFormat
                diffRow = diffRow + 1
            End If
            
            ' Formatting: Alignment
            If Not CompareAlignment(cellA, cellB) Then
                diffWs.Cells(diffRow, 1).Value = wsA.Name
                diffWs.Cells(diffRow, 2).Value = coord
                diffWs.Cells(diffRow, 3).Value = "Alignment"
                diffWs.Cells(diffRow, 4).Value = AlignmentToString(cellA)
                diffWs.Cells(diffRow, 5).Value = AlignmentToString(cellB)
                diffRow = diffRow + 1
            End If
            
            ' Formatting: Border (simple check)
            If Not CompareBorders(cellA.Borders, cellB.Borders) Then
                diffWs.Cells(diffRow, 1).Value = wsA.Name
                diffWs.Cells(diffRow, 2).Value = coord
                diffWs.Cells(diffRow, 3).Value = "Border"
                diffWs.Cells(diffRow, 4).Value = "See cell"
                diffWs.Cells(diffRow, 5).Value = "See cell"
                diffRow = diffRow + 1
            End If
        Next c
    Next r
    
    CompareSheetContent = summary
End Function

' Helper: Compare font objects
Function CompareFont(f1 As Font, f2 As Font) As Boolean
    CompareFont = (f1.Name = f2.Name) And (f1.Size = f2.Size) And (f1.Bold = f2.Bold) And (f1.Italic = f2.Italic) And (f1.Underline = f2.Underline) And (f1.Color = f2.Color)
End Function

' Helper: Font to string
Function FontToString(f As Font) As String
    FontToString = "Name:" & f.Name & ", Size:" & f.Size & ", Bold:" & f.Bold & ", Italic:" & f.Italic & ", Underline:" & f.Underline & ", Color:" & f.Color
End Function

' Helper: Compare alignment
Function CompareAlignment(cellA As Range, cellB As Range) As Boolean
    CompareAlignment = (cellA.HorizontalAlignment = cellB.HorizontalAlignment) And (cellA.VerticalAlignment = cellB.VerticalAlignment) And (cellA.WrapText = cellB.WrapText)
End Function

' Helper: Alignment to string
Function AlignmentToString(cell As Range) As String
    AlignmentToString = "H:" & cell.HorizontalAlignment & ", V:" & cell.VerticalAlignment & ", Wrap:" & cell.WrapText
End Function

' Helper: Compare borders (simple)
Function CompareBorders(b1 As Borders, b2 As Borders) As Boolean
    CompareBorders = True
    Dim side As Variant
    For Each side In Array(xlEdgeLeft, xlEdgeRight, xlEdgeTop, xlEdgeBottom)
        If b1(side).LineStyle <> b2(side).LineStyle Or b1(side).Color <> b2(side).Color Then
            CompareBorders = False
            Exit Function
        End If
    Next
End Function

' Helper: Check if cell has data validation
Function HasValidation(cell As Range) As Boolean
    On Error Resume Next
    HasValidation = Not cell.Validation Is Nothing
    On Error GoTo 0
End Function

' Helper: Get validation formula
Function GetValidationFormula(cell As Range) As String
    On Error Resume Next
    If Not cell.Validation Is Nothing Then
        GetValidationFormula = cell.Validation.Formula1
    Else
        GetValidationFormula = ""
    End If
    On Error GoTo 0
End Function 

' Compare all Excel files in two directories by name
Sub CompareExcelDirectories()
    Dim folderA As String, folderB As String
    Dim fso As Object, filesA As Object, filesB As Object
    Dim dictA As Object, dictB As Object
    Dim fileName As Variant
    Dim summaryWs As Worksheet
    Dim row As Long
    
    ' Prompt user for folder paths
    folderA = InputBox("Enter path to first folder:", "Folder A")
    folderB = InputBox("Enter path to second folder:", "Folder B")
    If folderA = "" Or folderB = "" Then Exit Sub
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set filesA = fso.GetFolder(folderA).Files
    Set filesB = fso.GetFolder(folderB).Files
    Set dictA = CreateObject("Scripting.Dictionary")
    Set dictB = CreateObject("Scripting.Dictionary")
    
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
    
    ' Create summary worksheet
    Set summaryWs = ThisWorkbook.Sheets.Add
    summaryWs.Name = "DirectoryCompareSummary"
    summaryWs.Cells(1, 1).Resize(1, 3).Value = Array("File Name", "Status", "Details")
    row = 2
    
    ' Files only in A
    For Each fileName In dictA.Keys
        If Not dictB.Exists(fileName) Then
            summaryWs.Cells(row, 1).Value = fileName
            summaryWs.Cells(row, 2).Value = "Only in Folder A"
            summaryWs.Cells(row, 3).Value = dictA(fileName)
            row = row + 1
        End If
    Next
    ' Files only in B
    For Each fileName In dictB.Keys
        If Not dictA.Exists(fileName) Then
            summaryWs.Cells(row, 1).Value = fileName
            summaryWs.Cells(row, 2).Value = "Only in Folder B"
            summaryWs.Cells(row, 3).Value = dictB(fileName)
            row = row + 1
        End If
    Next
    ' Files in both - compare
    For Each fileName In dictA.Keys
        If dictB.Exists(fileName) Then
            summaryWs.Cells(row, 1).Value = fileName
            summaryWs.Cells(row, 2).Value = "Compared"
            summaryWs.Cells(row, 3).Value = "See Differences sheet for details."
            row = row + 1
            ' Compare the files
            CompareWorkbooks dictA(fileName), dictB(fileName)
        End If
    Next
    summaryWs.Columns.AutoFit
    MsgBox "Directory comparison complete. See 'DirectoryCompareSummary' and 'Differences' sheets.", vbInformation
End Sub 
Add-Type -AssemblyName System.Drawing
$out = Join-Path (Get-Location) '02_Projects\AI-Career-Transition\10_学习文档\assets\P02A-03'
function Start-Figure($h) {
 $script:b = New-Object System.Drawing.Bitmap(1200,$h)
 $script:g = [System.Drawing.Graphics]::FromImage($b)
 $g.Clear([System.Drawing.Color]::White)
 $g.SmoothingMode='AntiAlias'
 $script:f = New-Object System.Drawing.Font('Microsoft YaHei',15)
 $script:big = New-Object System.Drawing.Font('Microsoft YaHei',22,[System.Drawing.FontStyle]::Bold)
}
function Txt($s,$x,$y,$large=$false) { $font=$f; if($large){$font=$big}; $g.DrawString($s,$font,[System.Drawing.Brushes]::Black,[single]$x,[single]$y) }
function Box($s,$x,$y,$w,$h,$color) {
 $brush=New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($color))
 $g.FillRectangle($brush,$x,$y,$w,$h); $g.DrawRectangle([System.Drawing.Pens]::SlateGray,$x,$y,$w,$h)
 Txt $s ($x+10) ($y+10); $brush.Dispose()
}
function Grid($name,$x,$y,$kind,$phase) {
 Txt $name $x ($y-35)
 for($r=0;$r -lt 4;$r++){for($c=0;$c -lt 4;$c++){
 $col='#F1F5F9'; if($kind -eq 'A' -and $r -lt 2 -and [math]::Floor($c/2) -eq $phase){$col='#BFDBFE'}
 if($kind -eq 'B' -and $c -lt 2 -and [math]::Floor($r/2) -eq $phase){$col='#A7F3D0'}
 if($kind -eq 'C' -and $r -lt 2 -and $c -lt 2){$col='#FDE68A'}
 Box ($kind+$r+$c) ($x+58*$c) ($y+45*$r) 58 45 $col
 }}
}
function Save-Figure($name){$b.Save((Join-Path $out $name),[System.Drawing.Imaging.ImageFormat]::Png);$g.Dispose();$b.Dispose()}
Start-Figure 680
Txt 'K 分块：输入块移动，输出块不动' 30 20 $true
Txt '4×4 矩阵；一个 block 负责 C 左上 2×2；每轮 K 取 2 个位置' 30 65
Grid '第 1 轮：k = 0, 1' 35 150 'A' 0
Grid 'B：取前两行' 410 150 'B' 0
Grid 'C：保留部分和' 825 150 'C' 0
Txt '×' 325 215 $true; Txt '累加 →' 675 215 $true
Grid '第 2 轮：k = 2, 3' 35 430 'A' 1
Grid 'B：取后两行' 410 430 'B' 1
Grid 'C：继续累加同一块' 825 430 'C' 1
Txt '×' 325 495 $true; Txt '累加 →' 675 495 $true
Txt 'A 沿列向右移动；B 沿行向下移动。两轮结束后才写回 C。' 35 635
Save-Figure 'k-tiling.png'
Start-Figure 690
Txt '同一批线程：加载时分工，计算时共享' 30 20 $true
Txt '只看第一轮 k = 0, 1；颜色区分 A 输入、B 输入和输出累加值' 30 65
Box "T0 搬入 A00、B00" 35 115 260 55 '#E2E8F0'
Box "T1 搬入 A01、B01" 325 115 260 55 '#E2E8F0'
Box "T2 搬入 A10、B10" 615 115 260 55 '#E2E8F0'
Box "T3 搬入 A11、B11" 905 115 260 55 '#E2E8F0'
Txt '↓ 写到 shared memory；等待本轮数据全部就绪 ↓' 265 190
Box 'A00 [T0]     A01 [T1]' 165 245 370 55 '#BFDBFE'
Box 'A10 [T2]     A11 [T3]' 165 300 370 55 '#BFDBFE'
Box 'B00 [T0]     B01 [T1]' 655 245 370 55 '#A7F3D0'
Box 'B10 [T2]     B11 [T3]' 655 300 370 55 '#A7F3D0'
Txt '↓ 按输出分工读取共享输入；不必只用自己搬入的元素 ↓' 245 385
Box 'T0: C00 += A00×B00 + A01×B10' 35 435 550 65 '#FDE68A'
Box 'T1: C01 += A00×B01 + A01×B11' 615 435 550 65 '#FDE68A'
Box 'T2: C10 += A10×B00 + A11×B10' 35 520 550 65 '#FDE68A'
Box 'T3: C11 += A10×B01 + A11×B11' 615 520 550 65 '#FDE68A'
Txt '跟踪 T0：A01 来自 T1，B10 来自 T2。搬入者与使用者不必相同。' 35 625
Save-Figure 'load-compute.png'
Start-Figure 450
Txt '对齐：需要的元素不变，覆盖的区间可能变多' 30 20 $true
Txt '沿用原图：每 4 个元素一组，仅用于演示区间边界，不代表硬件固定粒度' 30 70
for($i=0;$i -lt 12;$i++){
 $col=@('#DBEAFE','#D1FAE5','#FEF3C7')[[math]::Floor($i/4)]
 Box ([string]$i) (220+65*$i) 125 65 55 $col
}
Txt '起点 4：' 35 220
Box '需要 4  5  6  7 → 覆盖 1 个区间' 480 205 520 60 '#D1FAE5'
Txt '起点 5：' 35 300
Box '需要 5  6  7  8 → 覆盖 2 个区间' 480 285 520 60 '#FED7AA'
Txt '两次都只要 4 个元素；第二次跨过 7 / 8 之间的边界。' 220 385
Save-Figure 'alignment-explained.png'

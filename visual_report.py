"""Relatório visual de uma página, com números calculados pelo projeto."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape,A4
from reportlab.lib.utils import simpleSplit

def currency(cents):return f'R$ {cents/100:,.2f}'.replace(',','X').replace('.',',').replace('X','.')

def create_pdf(result,path,notes=None):
    width,height=landscape(A4)
    pdf=canvas.Canvas(str(path),pagesize=(width,height))
    pdf.setTitle('Pulso - Relatório de vendas com dados fictícios')
    paper,ink,muted,green=map(HexColor,('#f1f3ee','#24362d','#68756c','#5c886a'))
    pdf.setFillColor(paper);pdf.rect(0,0,width,height,fill=1,stroke=0)
    def text(x,y,value,size=10,color=ink,bold=False):
        pdf.setFillColor(color);pdf.setFont('Helvetica-Bold' if bold else 'Helvetica',size);pdf.drawString(x,y,str(value))
    def panel(x,y,w,h):
        pdf.setFillColor(HexColor('#ffffff'));pdf.roundRect(x,y,w,h,8,fill=1,stroke=0)
    text(34,554,'PULSO / DADOS + IA',10,green,True)
    text(34,522,'Vendas em uma página',27,ink,True)
    dates=[row[1] for row in result['cleaned_rows']]
    period=f'{min(dates)} a {max(dates)}' if dates else 'Sem vendas válidas'
    text(34,501,'Base fictícia para estudo | Período: '+period,10,muted)
    summary=result['summary']
    cards=[('RECEITA CONCLUÍDA',currency(summary['revenue_cents'])),('PEDIDOS CONCLUÍDOS',str(summary['completed_orders'])),('TICKET MÉDIO',currency(summary['average_order_cents']))]
    for i,(label,value) in enumerate(cards):
        x=34+i*260;panel(x,398,250,78);text(x+16,451,label,8,muted,True);text(x+16,419,value,25,ink,True)
    panel(34,189,440,190);text(50,355,'Qual categoria trouxe mais receita?',13,ink,True)
    maximum=max([r['revenue_cents'] for r in result['by_category']] or [1])
    for i,row in enumerate(result['by_category'][:4]):
        y=321-i*39;text(50,y,row['category'],10)
        pdf.setFillColor(HexColor('#e5ece6'));pdf.roundRect(166,y-3,193,12,3,fill=1,stroke=0)
        pdf.setFillColor(green);pdf.roundRect(166,y-3,max(2,193*row['revenue_cents']/maximum),12,3,fill=1,stroke=0)
        text(371,y,currency(row['revenue_cents']),9,muted)
    panel(491,189,317,190);text(507,355,'Receita por mês',13,ink,True)
    months=result['by_month'][:6];top=max([m['revenue_cents'] for m in months] or [1])
    for i,row in enumerate(months):
        y=323-i*24;text(507,y,row['month'],9)
        pdf.setFillColor(green);pdf.rect(565,y-1,130*row['revenue_cents']/top,9,fill=1,stroke=0)
        text(704,y,currency(row['revenue_cents']),8,muted)
    panel(34,52,774,120)
    heading='Leitura dos dados com IA - rascunho para revisão' if notes else 'Leitura dos dados - resumo por regras'
    text(50,148,heading,12,ink,True)
    if notes:
        prose=' '.join(item['comment'] for item in notes['observations'])
    else:
        top_category=result['by_category'][0]['category'] if result['by_category'] else 'Nenhuma categoria'
        prose=(f"{top_category} teve a maior receita no conjunto. {summary['cancelled_orders']} pedidos cancelados ficaram fora da receita. "
               f"{len(result['issues'])} linhas foram separadas para revisão antes da análise.")
    lines=simpleSplit(prose,'Helvetica',10,735)
    for i,line in enumerate(lines[:4]):text(50,126-i*14,line,10,muted)
    text(50,66,'IA opcional: o modelo recebe os indicadores; os cálculos permanecem em Python e SQL.',8,muted)
    text(34,28,'PROJETO DE ESTUDO PARA ESTÁGIO | Valores fictícios | Não representa resultado de empresa real',8,muted)
    pdf.save()

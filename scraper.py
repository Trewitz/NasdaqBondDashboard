# %%

from requests import Session, Response
from datetime import datetime
import pandas as pd

def convert_date(timestamp: float):
    return datetime.fromtimestamp(timestamp/1000)

class Bond:
    def __init__(
        self,
        id: str
    ) -> None:
        self.id = id

        self.df = None
        self.issuer = None
        self.coupon = None
        self.repayment = None

    def get_bond_data(self):
        with Session() as session:
            session.headers = {
                'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) '
                    'Gecko/20100101 '
                    'Firefox/96.0',
            }

            response = self._chart_data(session)
            resposne = self._meta_data(session)
    
    def _chart_data(self, session:Session):
        xml_query = f'''<post>
            <param name="SubSystem" value="History"/>
            <param name="Action" value="GetChartData"/>
            <param name="inst.an" value="id,nm,fnm,isin,tp,chp,ycp"/>
            <param name="Instrument" value="{self.id}"/>
            <param name="chart.an" value="atap,cp"/>
            <param name="FromDate" value="2007-07-11"/>
            <param name="json" value="1"/>
            <param name="app" value="/bonds/denmark/microsite"/>
            </post>
            '''
        response = self.__fetch_data(session, xml_query)
        response = response.json()['data']
        cp = response[0]['chartData']['cp']
        atap = response[0]['chartData']['atap']

        self.df = pd.merge(
            pd.DataFrame(cp, columns=['Date', 'Close']), 
            pd.DataFrame(atap, columns=['Date', 'AvgCPH']),
            how='left',
            on=['Date']
        )
        self.df['Date'] = self.df['Date'].apply(convert_date)

    def _meta_data(self, session:Session):
        xml_query = f'''<post>
            <param name="Exchange" value="NMF"/>
            <param name="SubSystem" value="Prices"/>
            <param name="Action" value="GetInstrument"/>
            <param name="inst__a" value="0,1,2,5,21,23"/>
            <param name="Exception" value="false"/>
            <param name="ext_xslt" value="/nordicV3/inst_table.xsl"/>
            <param name="Instrument" value="{self.id}"/>
            <param name="inst__an" value="id,nm,fnm,isin,chp,bp,ap,av,mtv,to,mhp,mlp,lsp,lv,op,cp,cpd,onexavg,onexv,corrbp,corrap,not,lcp,lcip,lcipd,ycd,isrid,lcpdt,lbbp,lbap,lop,lhp,llp,hp,lp,pavg,atap,patap,du,ytm,typ,cr,rl,ed,nvl,isr,dft,cpnrt,mktn,notetxt,oa,rpd,st,lt,rps,cc,rpr,dp,drd,dps,ec,lip,apatd,papatd,apadate,atv"/>
            <param name="inst__e" value="1,3,6,7,8"/>
            <param name="trd__a" value="7,8"/>
            <param name="t__a" value="1,2,10,7,8,18,31"/>
            <param name="json" value="1"/>
            <param name="app" value="/bonds/denmark/microsite"/>
            </post>'''
        response = self.__fetch_data(session, xml_query)
        response = response.json()['inst']

        self.issuer = response['@isr']
        self.coupon = response['@cpnrt']
        self.repayment = response['@rps']
        if response['@rps'] == 'Optional repayment':
            self.repayment = 'Optional'


    def __fetch_data(self, session: Session, xml_query: str, bond_type: str = 'doMortgageCreditAndSpecialInstitutions',) -> Response:
        with session.post(
            url='http://www.nasdaqomxnordic.com/webproxy/DataFeedProxy.aspx',
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
            },
            cookies={'bonds_dk_search_view': bond_type},
            data={'xmlquery': xml_query},
            #timeout=5,
        ) as resp:
            resp.raise_for_status()

        if resp.text == 'Invalid Request':
            raise APIError()
        return resp

if __name__ == '__main__':
    id = 'XCSE35NYK01EA53'
    bond = Bond(id)
    bond.get_bond_data()
    id_1 = 'XCSE35NYK01EDA53'
    bond_1 = Bond(id_1)
    bond_1.get_bond_data()

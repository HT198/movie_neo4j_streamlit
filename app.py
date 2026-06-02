import streamlit as st
from neo4j import GraphDatabase

# --------------------------
# 在这里填入你的 Neo4j Aura 信息
# --------------------------
NEO4J_URI = "neo4j+s://9941d4b7.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "LzrXQL2005011354321v"

# 连接数据库
@st.cache_resource
def get_driver():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return driver

driver = get_driver()

# 页面标题
st.title("🎬 电影知识图谱查询系统")
st.subheader("基于 Neo4j Aura + Streamlit")

# 侧边栏菜单
st.sidebar.title("📌 快速查询")

# 10条你已经设计好的查询语句
queries = {
    "1. 查看所有电影": "MATCH (m:`movie.csv`) RETURN m.name AS 电影名, m.rating AS 评分, m.year AS 年份",
    "2. 查看所有导演": "MATCH (d:`director.csv`) RETURN d.director_name AS 导演姓名",
    "3. 查看评分>8分的电影": "MATCH (m:`movie.csv`) WHERE m.rating>8 RETURN m.name, m.rating",
    "4. 查询《流浪地球》的导演": "MATCH (d)-[:DIRECTED]->(m:`movie.csv`{name:'流浪地球'}) RETURN d.director_name",
    "5. 查询郭帆的电影": "MATCH (d:`director.csv`{director_name:'郭帆'})-[:DIRECTED]->(m) RETURN m.name",
    "6. 查看完整导演-电影关系": "MATCH (d)-[r:DIRECTED]->(m) RETURN d, r, m",
    "7. 统计电影与导演总数": "MATCH (n) RETURN labels(n) AS 类型, count(n) AS 数量",
    "8. 统计每位导演作品数": "MATCH (d)-[:DIRECTED]->(m) RETURN d.director_name, count(m) AS 作品数",
    "9. 搜索含'地球'的电影": "MATCH (m:`movie.csv`) WHERE m.name CONTAINS '地球' RETURN m.name",
    "10. 2020年后的电影": "MATCH (m:`movie.csv`) WHERE m.year>=2020 RETURN m.name, m.year"
}

# 选择查询
option = st.sidebar.selectbox("选择查询语句", list(queries.keys()))

# 运行按钮
if st.sidebar.button("▶ 运行查询"):
    with driver.session() as session:
        result = session.run(queries[option])
        df = result.to_df()
        st.dataframe(df)

# 搜索框（加分项）
st.markdown("---")
st.subheader("🔍 实体搜索（导演/电影）")
keyword = st.text_input("输入名称")
if keyword:
    cypher = f"""
    MATCH (n)
    WHERE n.name CONTAINS '{keyword}' OR n.director_name CONTAINS '{keyword}'
    RETURN labels(n)[0] AS 类型, coalesce(n.name, n.director_name) AS 名称
    """
    with driver.session() as session:
        res = session.run(cypher)
        st.dataframe(res.to_df())

"""
情感分析师Agent

专门负责市场情感分析，包括新闻情感、社交媒体情感、市场情绪指标等
参考TradingAgents的情感分析实现，结合中文环境和A股市场特点
"""

from typing import Dict, Any, List
from ..base_agent import BaseAgent, AgentResponse
import json
import re
from datetime import datetime, timedelta


class SentimentAnalyst(BaseAgent):
    """情感分析师"""
    
    def __init__(self, agent_id: str, llm_adapter, config: Dict[str, Any] = None):
        super().__init__(agent_id, "情感分析师", llm_adapter, config)
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的市场情感分析师，专门分析市场情绪和投资者情感。

你的职责包括：
1. 新闻情感分析 - 分析相关新闻的情感倾向和影响
2. 市场情绪分析 - 评估整体市场情绪和投资者信心
3. 社交媒体情感 - 分析投资者在社交平台的讨论情感
4. 政策影响分析 - 评估政策变化对市场情感的影响
5. 情感指标计算 - 计算各种情感强度和方向指标

分析要求：
- 准确识别正面、负面和中性情感
- 量化情感强度和置信度
- 区分短期情绪波动和长期趋势
- 考虑中国市场特有的情感因素
- 结合技术指标验证情感信号

输出格式要求：
- 使用中文进行分析
- 提供情感得分和具体原因
- 明确区分不同来源的情感数据
- 给出情感驱动的交易建议"""

    def get_role_responsibility(self) -> str:
        """获取角色职责描述"""
        return "市场情绪、新闻情感和投资者信心分析"
    
    def get_required_inputs(self) -> List[str]:
        """获取必需的输入参数"""
        return ["sentiment_data", "symbol"]
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """验证输入参数"""
        required_fields = self.get_required_inputs()
        
        for field in required_fields:
            if field not in inputs:
                self.logger.error(f"缺少必需的输入参数: {field}")
                return False
        
        # 验证情感数据结构
        sentiment_data = inputs.get('sentiment_data', {})
        if not isinstance(sentiment_data, dict):
            self.logger.error("sentiment_data必须是字典类型")
            return False
        
        return True
    
    def process(self, inputs: Dict[str, Any]) -> AgentResponse:
        """处理分析请求"""
        if not self.validate_inputs(inputs):
            return self.format_output(
                content="输入参数验证失败",
                confidence=0.0,
                reasoning=["输入参数不完整或格式错误"]
            )
        
        symbol = inputs.get('symbol', '')
        sentiment_data = inputs.get('sentiment_data', {})
        
        try:
            # 分析情感数据
            analysis_results = self._analyze_sentiment(symbol, sentiment_data)
            
            # 生成分析请求
            analysis_request = self._format_analysis_request(symbol, analysis_results)
            
            # 调用LLM进行分析
            llm_response = self.llm_adapter.chat([
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": analysis_request}
            ])
            
            # 解析分析结果
            confidence, reasoning = self._parse_analysis_result(
                llm_response.content, analysis_results
            )
            
            self.logger.info(f"情感分析师完成 {symbol} 的分析，置信度: {confidence}")
            
            return self.format_output(
                content=llm_response.content,
                confidence=confidence,
                reasoning=reasoning,
                sentiment_analysis=analysis_results,
                llm_response=llm_response.content
            )
            
        except Exception as e:
            self.logger.error(f"情感分析失败: {e}")
            return self.format_output(
                content=f"情感分析遇到错误: {str(e)}",
                confidence=0.0,
                reasoning=[f"分析过程中出现错误: {str(e)}"]
            )
    
    def _analyze_sentiment(self, symbol: str, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析情感数据"""
        analysis = {
            'symbol': symbol,
            'news_sentiment': {},
            'social_sentiment': {},
            'market_sentiment': {},
            'policy_sentiment': {},
            'overall_sentiment': {}
        }
        
        try:
            # 新闻情感分析
            if 'news' in sentiment_data:
                analysis['news_sentiment'] = self._analyze_news_sentiment(sentiment_data['news'])
            
            # 社交媒体情感分析
            if 'social_media' in sentiment_data:
                analysis['social_sentiment'] = self._analyze_social_sentiment(sentiment_data['social_media'])
            
            # 市场情感分析
            if 'market_indicators' in sentiment_data:
                analysis['market_sentiment'] = self._analyze_market_sentiment(sentiment_data['market_indicators'])
            
            # 政策情感分析
            if 'policy_news' in sentiment_data:
                analysis['policy_sentiment'] = self._analyze_policy_sentiment(sentiment_data['policy_news'])
            
            # 综合情感分析
            analysis['overall_sentiment'] = self._calculate_overall_sentiment(analysis)
            
        except Exception as e:
            self.logger.error(f"情感数据分析失败: {e}")
        
        return analysis
    
    def _analyze_news_sentiment(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析新闻情感"""
        sentiment_scores = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        important_news = []
        
        for news_item in news_data:
            try:
                # 提取新闻标题和内容
                title = news_item.get('title', '')
                content = news_item.get('content', '')
                source = news_item.get('source', '')
                timestamp = news_item.get('timestamp', '')
                
                # 计算情感得分
                sentiment_score = self._calculate_news_sentiment_score(title, content)
                sentiment_scores.append(sentiment_score)
                
                # 分类统计
                if sentiment_score > 0.2:
                    positive_count += 1
                elif sentiment_score < -0.2:
                    negative_count += 1
                else:
                    neutral_count += 1
                
                # 识别重要新闻
                if abs(sentiment_score) > 0.5:
                    important_news.append({
                        'title': title,
                        'sentiment_score': sentiment_score,
                        'source': source,
                        'impact_level': self._evaluate_news_impact(sentiment_score, source)
                    })
                    
            except Exception as e:
                self.logger.error(f"新闻情感分析错误: {e}")
                continue
        
        # 计算综合指标
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        sentiment_volatility = self._calculate_sentiment_volatility(sentiment_scores)
        
        return {
            'average_sentiment': avg_sentiment,
            'sentiment_volatility': sentiment_volatility,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_news': len(news_data),
            'important_news': important_news[:5],  # 只保留前5条重要新闻
            'sentiment_trend': self._evaluate_news_sentiment_trend(avg_sentiment)
        }
    
    def _analyze_social_sentiment(self, social_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析社交媒体情感"""
        sentiment_metrics = {}
        
        try:
            # 微博情感
            if 'weibo' in social_data:
                weibo_sentiment = self._analyze_platform_sentiment(social_data['weibo'], 'weibo')
                sentiment_metrics['weibo'] = weibo_sentiment
            
            # 股吧情感
            if 'guba' in social_data:
                guba_sentiment = self._analyze_platform_sentiment(social_data['guba'], 'guba')
                sentiment_metrics['guba'] = guba_sentiment
            
            # 雪球情感
            if 'xueqiu' in social_data:
                xueqiu_sentiment = self._analyze_platform_sentiment(social_data['xueqiu'], 'xueqiu')
                sentiment_metrics['xueqiu'] = xueqiu_sentiment
            
            # 综合社交情感
            if sentiment_metrics:
                overall_social = self._aggregate_social_sentiment(sentiment_metrics)
                sentiment_metrics['overall'] = overall_social
                
        except Exception as e:
            self.logger.error(f"社交媒体情感分析错误: {e}")
        
        return sentiment_metrics
    
    def _analyze_platform_sentiment(self, platform_data: List[Dict[str, Any]], platform_name: str) -> Dict[str, Any]:
        """分析单个平台的情感"""
        sentiment_scores = []
        engagement_scores = []
        
        for post in platform_data:
            try:
                content = post.get('content', '')
                likes = post.get('likes', 0)
                comments = post.get('comments', 0)
                shares = post.get('shares', 0)
                
                # 计算情感得分
                sentiment_score = self._calculate_text_sentiment_score(content)
                sentiment_scores.append(sentiment_score)
                
                # 计算参与度得分
                engagement = self._calculate_engagement_score(likes, comments, shares)
                engagement_scores.append(engagement)
                
            except Exception as e:
                self.logger.error(f"{platform_name}情感分析错误: {e}")
                continue
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        
        return {
            'average_sentiment': avg_sentiment,
            'average_engagement': avg_engagement,
            'post_count': len(platform_data),
            'sentiment_distribution': self._get_sentiment_distribution(sentiment_scores),
            'platform': platform_name
        }
    
    def _analyze_market_sentiment(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场情感指标"""
        market_sentiment = {}
        
        try:
            # VIX恐慌指数
            if 'vix' in market_data and market_data['vix'] is not None:
                vix = float(market_data['vix'])
                market_sentiment['vix'] = vix
                market_sentiment['fear_level'] = self._evaluate_vix_level(vix)
            
            # 涨跌家数比
            if 'advance_decline_ratio' in market_data and market_data['advance_decline_ratio'] is not None:
                ad_ratio = float(market_data['advance_decline_ratio'])
                market_sentiment['advance_decline_ratio'] = ad_ratio
                market_sentiment['breadth_sentiment'] = self._evaluate_breadth_sentiment(ad_ratio)
            
            # 资金流向
            if 'money_flow' in market_data and market_data['money_flow'] is not None:
                money_flow = float(market_data['money_flow'])
                market_sentiment['money_flow'] = money_flow
                market_sentiment['flow_sentiment'] = self._evaluate_money_flow_sentiment(money_flow)
            
            # 融资融券比例
            if 'margin_ratio' in market_data and market_data['margin_ratio'] is not None:
                margin_ratio = float(market_data['margin_ratio'])
                market_sentiment['margin_ratio'] = margin_ratio
                market_sentiment['leverage_sentiment'] = self._evaluate_leverage_sentiment(margin_ratio)
            
        except Exception as e:
            self.logger.error(f"市场情感指标分析错误: {e}")
        
        return market_sentiment
    
    def _analyze_policy_sentiment(self, policy_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析政策情感"""
        policy_sentiment = {
            'recent_policies': [],
            'overall_policy_tone': 0,
            'policy_impact_level': 'neutral'
        }
        
        policy_scores = []
        
        for policy_item in policy_data:
            try:
                title = policy_item.get('title', '')
                content = policy_item.get('content', '')
                category = policy_item.get('category', '')
                importance = policy_item.get('importance', 'medium')
                
                # 计算政策情感得分
                sentiment_score = self._calculate_policy_sentiment_score(title, content, category)
                policy_scores.append(sentiment_score)
                
                policy_sentiment['recent_policies'].append({
                    'title': title,
                    'category': category,
                    'sentiment_score': sentiment_score,
                    'importance': importance,
                    'impact_direction': self._get_policy_impact_direction(sentiment_score)
                })
                
            except Exception as e:
                self.logger.error(f"政策情感分析错误: {e}")
                continue
        
        if policy_scores:
            policy_sentiment['overall_policy_tone'] = sum(policy_scores) / len(policy_scores)
            policy_sentiment['policy_impact_level'] = self._evaluate_policy_impact_level(
                policy_sentiment['overall_policy_tone']
            )
        
        return policy_sentiment
    
    def _calculate_overall_sentiment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """计算综合情感得分"""
        sentiment_components = []
        weights = []
        
        # 新闻情感权重：30%
        if analysis['news_sentiment']:
            news_score = analysis['news_sentiment'].get('average_sentiment', 0)
            sentiment_components.append(news_score)
            weights.append(0.3)
        
        # 社交情感权重：25%
        if analysis['social_sentiment'] and 'overall' in analysis['social_sentiment']:
            social_score = analysis['social_sentiment']['overall'].get('average_sentiment', 0)
            sentiment_components.append(social_score)
            weights.append(0.25)
        
        # 市场情感权重：30%
        if analysis['market_sentiment']:
            market_score = self._convert_market_sentiment_to_score(analysis['market_sentiment'])
            sentiment_components.append(market_score)
            weights.append(0.3)
        
        # 政策情感权重：15%
        if analysis['policy_sentiment']:
            policy_score = analysis['policy_sentiment'].get('overall_policy_tone', 0)
            sentiment_components.append(policy_score)
            weights.append(0.15)
        
        # 计算加权平均
        if sentiment_components:
            weighted_sentiment = sum(score * weight for score, weight in zip(sentiment_components, weights))
            total_weight = sum(weights)
            overall_score = weighted_sentiment / total_weight if total_weight > 0 else 0
        else:
            overall_score = 0
        
        return {
            'overall_score': overall_score,
            'sentiment_level': self._evaluate_overall_sentiment_level(overall_score),
            'components_count': len(sentiment_components),
            'confidence_level': min(1.0, len(sentiment_components) / 4)  # 最多4个组件
        }
    
    def _calculate_news_sentiment_score(self, title: str, content: str) -> float:
        """计算新闻情感得分"""
        # 正面关键词
        positive_keywords = [
            '利好', '上涨', '增长', '盈利', '突破', '创新', '合作', '签约', '中标',
            '业绩', '分红', '回购', '重组', '并购', '扩张', '投资', '机会', '优势'
        ]
        
        # 负面关键词
        negative_keywords = [
            '利空', '下跌', '下滑', '亏损', '风险', '警告', '调查', '处罚', '诉讼',
            '债务', '违约', '停牌', '退市', '减持', '裁员', '关闭', '困难', '危机'
        ]
        
        text = (title + ' ' + content).lower()
        
        positive_score = sum(1 for keyword in positive_keywords if keyword in text)
        negative_score = sum(1 for keyword in negative_keywords if keyword in text)
        
        # 标题权重更高
        title_positive = sum(1 for keyword in positive_keywords if keyword in title.lower())
        title_negative = sum(1 for keyword in negative_keywords if keyword in title.lower())
        
        total_positive = positive_score + title_positive * 1.5
        total_negative = negative_score + title_negative * 1.5
        
        # 归一化到[-1, 1]范围
        if total_positive + total_negative == 0:
            return 0
        
        sentiment_score = (total_positive - total_negative) / (total_positive + total_negative)
        return max(-1, min(1, sentiment_score))
    
    def _calculate_text_sentiment_score(self, text: str) -> float:
        """计算文本情感得分（简化版本）"""
        # 这里使用简化的关键词匹配方法
        # 实际应用中可以使用更复杂的情感分析模型
        return self._calculate_news_sentiment_score(text, '')
    
    def _calculate_engagement_score(self, likes: int, comments: int, shares: int) -> float:
        """计算参与度得分"""
        # 简化的参与度计算
        engagement = likes * 1 + comments * 2 + shares * 3
        return min(100, engagement / 10)  # 归一化到0-100
    
    def _get_sentiment_distribution(self, sentiment_scores: List[float]) -> Dict[str, int]:
        """获取情感分布"""
        positive = sum(1 for score in sentiment_scores if score > 0.2)
        negative = sum(1 for score in sentiment_scores if score < -0.2)
        neutral = len(sentiment_scores) - positive - negative
        
        return {
            'positive': positive,
            'negative': negative,
            'neutral': neutral
        }
    
    def _aggregate_social_sentiment(self, sentiment_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """聚合社交媒体情感"""
        total_sentiment = 0
        total_posts = 0
        platform_count = 0
        
        for platform_name, platform_data in sentiment_metrics.items():
            if isinstance(platform_data, dict):
                sentiment = platform_data.get('average_sentiment', 0)
                posts = platform_data.get('post_count', 0)
                
                total_sentiment += sentiment * posts
                total_posts += posts
                platform_count += 1
        
        avg_sentiment = total_sentiment / total_posts if total_posts > 0 else 0
        
        return {
            'average_sentiment': avg_sentiment,
            'total_posts': total_posts,
            'platforms_count': platform_count
        }
    
    def _convert_market_sentiment_to_score(self, market_sentiment: Dict[str, Any]) -> float:
        """将市场情感指标转换为得分"""
        score = 0
        factor_count = 0
        
        # VIX指标（反向）
        if 'vix' in market_sentiment:
            vix = market_sentiment['vix']
            if vix < 20:
                score += 0.3  # 低恐慌
            elif vix > 30:
                score -= 0.3  # 高恐慌
            factor_count += 1
        
        # 涨跌家数比
        if 'advance_decline_ratio' in market_sentiment:
            ad_ratio = market_sentiment['advance_decline_ratio']
            if ad_ratio > 1.5:
                score += 0.4
            elif ad_ratio < 0.5:
                score -= 0.4
            factor_count += 1
        
        # 资金流向
        if 'money_flow' in market_sentiment:
            money_flow = market_sentiment['money_flow']
            if money_flow > 0:
                score += 0.3 * min(money_flow / 1000000000, 1)  # 按十亿归一化
            else:
                score += 0.3 * max(money_flow / 1000000000, -1)
            factor_count += 1
        
        return score / factor_count if factor_count > 0 else 0
    
    def _calculate_sentiment_volatility(self, scores: List[float]) -> float:
        """计算情感波动率"""
        if len(scores) < 2:
            return 0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        return variance ** 0.5
    
    def _calculate_policy_sentiment_score(self, title: str, content: str, category: str) -> float:
        """计算政策情感得分"""
        # 政策相关的正面关键词
        policy_positive = [
            '支持', '鼓励', '促进', '优化', '减税', '降费', '补贴', '扶持',
            '开放', '便民', '利好', '改革', '创新', '发展', '增长'
        ]
        
        # 政策相关的负面关键词
        policy_negative = [
            '限制', '禁止', '严控', '监管', '处罚', '调控', '紧缩',
            '征税', '加税', '整顿', '清理', '关停', '压缩'
        ]
        
        text = (title + ' ' + content).lower()
        
        positive_count = sum(1 for keyword in policy_positive if keyword in text)
        negative_count = sum(1 for keyword in policy_negative if keyword in text)
        
        if positive_count + negative_count == 0:
            return 0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    # 评估函数
    def _evaluate_news_impact(self, sentiment_score: float, source: str) -> str:
        """评估新闻影响级别"""
        base_impact = abs(sentiment_score)
        
        # 权威媒体权重更高
        authoritative_sources = ['新华社', '人民日报', '央视', '证券时报', '上证报']
        if any(auth_source in source for auth_source in authoritative_sources):
            base_impact *= 1.5
        
        if base_impact > 0.8:
            return '重大影响'
        elif base_impact > 0.6:
            return '较大影响'
        elif base_impact > 0.3:
            return '一般影响'
        else:
            return '轻微影响'
    
    def _evaluate_news_sentiment_trend(self, avg_sentiment: float) -> str:
        """评估新闻情感趋势"""
        if avg_sentiment > 0.3:
            return '明显正面'
        elif avg_sentiment > 0.1:
            return '偏向正面'
        elif avg_sentiment > -0.1:
            return '中性'
        elif avg_sentiment > -0.3:
            return '偏向负面'
        else:
            return '明显负面'
    
    def _evaluate_vix_level(self, vix: float) -> str:
        """评估VIX恐慌水平"""
        if vix < 15:
            return '极度乐观'
        elif vix < 20:
            return '乐观'
        elif vix < 25:
            return '正常'
        elif vix < 30:
            return '担忧'
        else:
            return '恐慌'
    
    def _evaluate_breadth_sentiment(self, ratio: float) -> str:
        """评估市场广度情感"""
        if ratio > 2.0:
            return '全面上涨'
        elif ratio > 1.5:
            return '普涨'
        elif ratio > 1.0:
            return '略偏强'
        elif ratio > 0.5:
            return '略偏弱'
        else:
            return '普跌'
    
    def _evaluate_money_flow_sentiment(self, flow: float) -> str:
        """评估资金流向情感"""
        if flow > 1000000000:  # 10亿以上
            return '大幅净流入'
        elif flow > 0:
            return '净流入'
        elif flow > -1000000000:
            return '净流出'
        else:
            return '大幅净流出'
    
    def _evaluate_leverage_sentiment(self, ratio: float) -> str:
        """评估杠杆情感"""
        if ratio > 0.15:
            return '高杠杆风险'
        elif ratio > 0.10:
            return '中等杠杆'
        elif ratio > 0.05:
            return '低杠杆'
        else:
            return '极低杠杆'
    
    def _evaluate_policy_impact_level(self, score: float) -> str:
        """评估政策影响级别"""
        if score > 0.5:
            return '重大利好'
        elif score > 0.2:
            return '一般利好'
        elif score > -0.2:
            return '中性'
        elif score > -0.5:
            return '一般利空'
        else:
            return '重大利空'
    
    def _evaluate_overall_sentiment_level(self, score: float) -> str:
        """评估综合情感水平"""
        if score > 0.4:
            return '极度乐观'
        elif score > 0.2:
            return '乐观'
        elif score > 0.1:
            return '偏乐观'
        elif score > -0.1:
            return '中性'
        elif score > -0.2:
            return '偏悲观'
        elif score > -0.4:
            return '悲观'
        else:
            return '极度悲观'
    
    def _get_policy_impact_direction(self, score: float) -> str:
        """获取政策影响方向"""
        if score > 0.1:
            return '利好'
        elif score < -0.1:
            return '利空'
        else:
            return '中性'
    
    def _format_analysis_request(self, symbol: str, analysis_results: Dict[str, Any]) -> str:
        """格式化分析请求"""
        request = f"""请分析股票 {symbol} 的市场情感情况：

情感数据分析：
"""
        
        # 新闻情感
        news_sentiment = analysis_results.get('news_sentiment', {})
        if news_sentiment:
            request += f"新闻情感：\n"
            request += f"平均情感得分: {news_sentiment.get('average_sentiment', 0):.3f}\n"
            request += f"情感趋势: {news_sentiment.get('sentiment_trend', 'N/A')}\n"
            request += f"正面新闻: {news_sentiment.get('positive_count', 0)}条\n"
            request += f"负面新闻: {news_sentiment.get('negative_count', 0)}条\n"
            request += f"中性新闻: {news_sentiment.get('neutral_count', 0)}条\n"
            
            if news_sentiment.get('important_news'):
                request += "重要新闻:\n"
                for news in news_sentiment['important_news'][:3]:
                    request += f"- {news['title']} (情感: {news['sentiment_score']:.2f}, 影响: {news['impact_level']})\n"
        
        # 社交媒体情感
        social_sentiment = analysis_results.get('social_sentiment', {})
        if social_sentiment and 'overall' in social_sentiment:
            overall_social = social_sentiment['overall']
            request += f"\n社交媒体情感：\n"
            request += f"平均情感得分: {overall_social.get('average_sentiment', 0):.3f}\n"
            request += f"总讨论数: {overall_social.get('total_posts', 0)}条\n"
            request += f"覆盖平台: {overall_social.get('platforms_count', 0)}个\n"
        
        # 市场情感
        market_sentiment = analysis_results.get('market_sentiment', {})
        if market_sentiment:
            request += f"\n市场情感指标：\n"
            if 'vix' in market_sentiment:
                request += f"恐慌指数(VIX): {market_sentiment['vix']:.2f} ({market_sentiment.get('fear_level', 'N/A')})\n"
            if 'advance_decline_ratio' in market_sentiment:
                request += f"涨跌比: {market_sentiment['advance_decline_ratio']:.2f} ({market_sentiment.get('breadth_sentiment', 'N/A')})\n"
            if 'money_flow' in market_sentiment:
                request += f"资金流向: {market_sentiment['money_flow']/100000000:.1f}亿 ({market_sentiment.get('flow_sentiment', 'N/A')})\n"
        
        # 政策情感
        policy_sentiment = analysis_results.get('policy_sentiment', {})
        if policy_sentiment:
            request += f"\n政策情感：\n"
            request += f"政策基调: {policy_sentiment.get('overall_policy_tone', 0):.3f}\n"
            request += f"影响级别: {policy_sentiment.get('policy_impact_level', 'N/A')}\n"
        
        # 综合情感
        overall_sentiment = analysis_results.get('overall_sentiment', {})
        if overall_sentiment:
            request += f"\n综合情感：\n"
            request += f"综合得分: {overall_sentiment.get('overall_score', 0):.3f}\n"
            request += f"情感水平: {overall_sentiment.get('sentiment_level', 'N/A')}\n"
            request += f"置信度: {overall_sentiment.get('confidence_level', 0):.2f}\n"
        
        request += """
请基于以上情感数据，从以下几个方面进行分析：
1. 市场情绪总体评估（乐观/悲观程度）
2. 情感驱动因素识别（主要正面/负面因素）
3. 情感强度和持续性判断
4. 情感与价格走势的关联性分析
5. 情感反转信号识别
6. 基于情感分析的交易时机建议

请给出具体的情感分析结论和交易建议。
"""
        
        return request
    
    def _parse_analysis_result(self, analysis_content: str, analysis_results: Dict[str, Any]) -> tuple:
        """解析分析结果，提取置信度和推理过程"""
        reasoning = []
        confidence = 0.5  # 默认置信度
        
        # 基于情感指标计算基础置信度
        confidence_factors = []
        
        # 综合情感因子
        overall_sentiment = analysis_results.get('overall_sentiment', {})
        if 'overall_score' in overall_sentiment:
            sentiment_score = overall_sentiment['overall_score']
            if abs(sentiment_score) > 0.3:
                confidence_factors.append(0.2 * abs(sentiment_score))
                direction = "正面" if sentiment_score > 0 else "负面"
                reasoning.append(f"市场情感{direction}({sentiment_score:.2f})")
        
        # 新闻情感因子
        news_sentiment = analysis_results.get('news_sentiment', {})
        if 'average_sentiment' in news_sentiment:
            news_score = news_sentiment['average_sentiment']
            if abs(news_score) > 0.2:
                confidence_factors.append(0.1 * abs(news_score))
                reasoning.append(f"新闻情感倾向明显({news_score:.2f})")
        
        # 市场技术情感因子
        market_sentiment = analysis_results.get('market_sentiment', {})
        if 'vix' in market_sentiment:
            vix = market_sentiment['vix']
            if vix > 30:  # 高恐慌
                confidence_factors.append(0.15)
                reasoning.append("市场恐慌情绪高涨")
            elif vix < 15:  # 极度乐观
                confidence_factors.append(0.1)
                reasoning.append("市场过度乐观")
        
        # 数据完整性因子
        components_count = overall_sentiment.get('components_count', 0)
        if components_count >= 3:
            confidence_factors.append(0.1)
            reasoning.append("情感数据来源充分")
        
        # 计算最终置信度
        confidence = 0.5 + sum(confidence_factors)
        confidence = max(0.1, min(0.9, confidence))  # 限制在0.1-0.9之间
        
        return confidence, reasoning
import { Favicon } from '@/components/Favicon';
import type { SourceItem } from '@/types';
import { formatDate, parseDate } from '@/utils/time';
import {
  ClockCircleOutlined,
  FlagOutlined,
  GlobalOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { Card, Flex, Space, Tag, Typography } from 'antd';
import { useInView } from 'react-intersection-observer';
import { SourceFeatureIcons } from './SourceFeatureIcons';
import { getLanguageLabel } from './utils';

export const SupportedSourceItem: React.FC<{
  source: SourceItem;
  disabled?: boolean;
}> = ({ source, disabled }) => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    rootMargin: '5px',
  });

  const updatedAt = formatDate(parseDate(Number(source.version) * 1000));

  return (
    <Card ref={ref} size="small" style={{ opacity: disabled ? 0.8 : 1 }}>
      <Flex align="center" gap={5} wrap>
        <Space style={{ flex: 1 }}>
          {inView && (
            <Favicon
              url={source.url}
              style={{ backgroundColor: '#39f' }}
              icon={disabled ? <StopOutlined /> : <GlobalOutlined />}
            />
          )}
          <Flex vertical>
            <Typography.Link
              strong
              delete={disabled}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              style={{ whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}
            >
              <Space size="small">
                {source.url}
                {source.total_novels > 0 && (
                  <Typography.Text type="secondary">
                    ({source.total_novels} novels)
                  </Typography.Text>
                )}
              </Space>
            </Typography.Link>
            {disabled && source.disable_reason && (
              <Typography.Text type="secondary">
                {source.disable_reason}
              </Typography.Text>
            )}
          </Flex>
        </Space>
        {source.language && (
          <Flex gap={7} align="center" justify="flex-end" style={{ flex: 1 }}>
            <SourceFeatureIcons source={source} />
            <Tag icon={<FlagOutlined />} title="Language">
              {getLanguageLabel(source.language)}
            </Tag>
            <Tag color="cyan" icon={<ClockCircleOutlined />} title="Updated At">
              {updatedAt}
            </Tag>
            <Tag color="green" title="Total Commits">
              {source.total_commits} commits
            </Tag>
          </Flex>
        )}
      </Flex>
    </Card>
  );
};

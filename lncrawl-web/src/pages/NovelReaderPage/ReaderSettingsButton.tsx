import { Reader } from '@/store/_reader';
import { FontFamily, ReaderTheme } from '@/types';
import {
  BgColorsOutlined,
  CheckOutlined,
  FontColorsOutlined,
  FontSizeOutlined,
  LineHeightOutlined,
  MinusOutlined,
  PlusOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import {
  Avatar,
  Button,
  Descriptions,
  Divider,
  Flex,
  Grid,
  Modal,
  Popover,
  Select,
  Slider,
  Space,
  Typography,
} from 'antd';
import { isEqual, startCase } from 'lodash';
import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

export const ReaderSettingsButton: React.FC<any> = () => {
  const dispatch = useDispatch();
  const { sm } = Grid.useBreakpoint();

  const [open, setOpen] = useState<boolean>(false);

  const theme = useSelector(Reader.select.theme);
  const fontSize = useSelector(Reader.select.fontSize);
  const lineHeight = useSelector(Reader.select.lineHeight);
  const fontFamily = useSelector(Reader.select.fontFamily);

  const updateTheme = (value: ReaderTheme) => {
    dispatch(Reader.action.setColor(value));
  };
  const updateFontSize = (value: number) => {
    dispatch(Reader.action.setFontSize(value));
  };
  const updateLineHeight = (value: number) => {
    dispatch(Reader.action.setLineHeight(value));
  };
  const updateFontFamily = (value: FontFamily) => {
    dispatch(Reader.action.setFontFamily(value));
  };

  return (
    <>
      <Button
        size="large"
        style={{ borderRadius: 0 }}
        icon={<SettingOutlined />}
        onClick={() => setOpen(true)}
      >
        {sm && 'Settings'}
      </Button>

      <Modal
        closable
        open={open}
        footer={null}
        destroyOnHidden
        title="Reader Settings"
        onCancel={() => setOpen(false)}
        styles={{
          header: { paddingBottom: 10 },
        }}
      >
        <Descriptions
          bordered
          column={1}
          size="small"
          items={[
            {
              label: (
                <>
                  <BgColorsOutlined /> Theme
                </>
              ),
              children: (
                <Space>
                  {Object.entries(ReaderTheme).map(([name, value]) => (
                    <Popover content={startCase(name)}>
                      <Avatar
                        style={{ ...value, cursor: 'pointer' }}
                        onClick={() => updateTheme(value)}
                        icon={isEqual(theme, value) && <CheckOutlined />}
                      />
                    </Popover>
                  ))}
                </Space>
              ),
            },
            {
              label: (
                <>
                  <FontColorsOutlined /> Font Family
                </>
              ),
              children: (
                <Select
                  variant="borderless"
                  style={{ width: '100%' }}
                  value={fontFamily}
                  onSelect={updateFontFamily}
                  options={Object.entries(FontFamily).map(([name, value]) => ({
                    value,
                    label: (
                      <span style={{ fontFamily: value }}>
                        {startCase(name)}
                      </span>
                    ),
                  }))}
                />
              ),
            },
            {
              label: (
                <>
                  <FontSizeOutlined /> Font Size
                </>
              ),
              children: (
                <Flex align="center" justify="space-around">
                  <Button
                    type="text"
                    shape="round"
                    style={{ width: '100%' }}
                    onClick={() => updateFontSize(fontSize - 1)}
                  >
                    <MinusOutlined />
                  </Button>
                  <Divider type="vertical" />
                  <Typography.Text
                    style={{
                      width: '100%',
                      fontWeight: 600,
                      textAlign: 'center',
                    }}
                  >
                    {fontSize}px
                  </Typography.Text>
                  <Divider type="vertical" />
                  <Button
                    type="text"
                    shape="round"
                    style={{ width: '100%' }}
                    onClick={() => updateFontSize(fontSize + 1)}
                  >
                    <PlusOutlined />
                  </Button>
                </Flex>
              ),
            },
            {
              label: (
                <>
                  <LineHeightOutlined /> Line Height
                </>
              ),
              children: (
                <Slider
                  min={0.5}
                  max={2.5}
                  step={0.05}
                  value={lineHeight}
                  onChange={updateLineHeight}
                />
              ),
            },
          ]}
        />
      </Modal>
    </>
  );
};

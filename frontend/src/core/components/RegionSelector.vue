<template>
  <div class="region-selector">
    <div class="grid grid-cols-3 gap-2">
      <!-- 省份 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">省份</label>
        <select
          :value="modelValue.province"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          @change="handleProvinceChange"
        >
          <option value="">请选择</option>
          <option v-for="province in provinces" :key="province" :value="province">
            {{ province }}
          </option>
        </select>
      </div>

      <!-- 城市 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">城市</label>
        <select
          :value="modelValue.city"
          :disabled="!modelValue.province"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100"
          @change="handleCityChange"
        >
          <option value="">请选择</option>
          <option v-for="city in cities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>
      </div>

      <!-- 区县 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">区县</label>
        <select
          :value="modelValue.district"
          :disabled="!modelValue.city"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100"
          @change="handleDistrictChange"
        >
          <option value="">请选择</option>
          <option v-for="district in districts" :key="district" :value="district">
            {{ district }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface RegionValue {
  province: string
  city: string
  district: string
}

interface Props {
  modelValue: RegionValue
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: RegionValue]
}>()

// 中国省市区数据（简化版，实际应用中应使用完整数据）
const regionData: Record<string, Record<string, string[]>> = {
  '北京市': {
    '北京市': ['东城区', '西城区', '朝阳区', '丰台区', '石景山区', '海淀区', '门头沟区', '房山区', '通州区', '顺义区', '昌平区', '大兴区', '怀柔区', '平谷区', '密云区', '延庆区'],
  },
  '上海市': {
    '上海市': ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区', '闵行区', '宝山区', '嘉定区', '浦东新区', '金山区', '松江区', '青浦区', '奉贤区', '崇明区'],
  },
  '广东省': {
    '广州市': ['天河区', '越秀区', '海珠区', '荔湾区', '白云区', '黄埔区', '番禺区', '花都区', '南沙区', '从化区', '增城区'],
    '深圳市': ['罗湖区', '福田区', '南山区', '盐田区', '宝安区', '龙岗区', '龙华区', '坪山区', '光明区', '大鹏新区'],
    '珠海市': ['香洲区', '斗门区', '金湾区'],
    '汕头市': ['龙湖区', '金平区', '濠江区', '潮阳区', '潮南区', '澄海区', '南澳县'],
    '佛山市': ['禅城区', '南海区', '顺德区', '高明区', '三水区'],
    '韶关市': ['武江区', '浈江区', '曲江区', '始兴县', '仁化县', '翁源县', '乳源瑶族自治县', '新丰县', '乐昌市', '南雄市'],
    '湛江市': ['赤坎区', '霞山区', '坡头区', '麻章区', '遂溪县', '徐闻县', '廉江市', '雷州市', '吴川市'],
    '肇庆市': ['端州区', '鼎湖区', '高要区', '广宁县', '怀集县', '封开县', '德庆县', '四会市'],
    '江门市': ['蓬江区', '江海区', '新会区', '台山市', '开平市', '鹤山市', '恩平市'],
    '茂名市': ['茂南区', '电白区', '高州市', '化州市', '信宜市'],
    '惠州市': ['惠城区', '惠阳区', '博罗县', '惠东县', '龙门县'],
    '梅州市': ['梅江区', '梅县区', '大埔县', '丰顺县', '五华县', '平远县', '蕉岭县', '兴宁市'],
    '汕尾市': ['城区', '海丰县', '陆河县', '陆丰市'],
    '河源市': ['源城区', '东源县', '和平县', '龙川县', '紫金县', '连平县'],
    '阳江市': ['江城区', '阳东区', '阳西县', '阳春市'],
    '清远市': ['清城区', '清新区', '佛冈县', '阳山县', '连山壮族瑶族自治县', '连南瑶族自治县', '英德市', '连州市'],
    '东莞市': ['东莞市'],
    '中山市': ['中山市'],
    '潮州市': ['湘桥区', '潮安区', '饶平县'],
    '揭阳市': ['榕城区', '揭东区', '揭西县', '惠来县', '普宁市'],
    '云浮市': ['云城区', '云安区', '新兴县', '郁南县', '罗定市'],
  },
  '浙江省': {
    '杭州市': ['拱墅区', '上城区', '西湖区', '滨江区', '萧山区', '余杭区', '临平区', '钱塘区', '富阳区', '临安区', '桐庐县', '淳安县', '建德市'],
    '宁波市': ['海曙区', '江北区', '北仑区', '镇海区', '鄞州区', '奉化区', '象山县', '宁海县', '余姚市', '慈溪市'],
    '温州市': ['鹿城区', '龙湾区', '瓯海区', '洞头区', '永嘉县', '平阳县', '苍南县', '文成县', '泰顺县', '瑞安市', '乐清市'],
    '嘉兴市': ['南湖区', '秀洲区', '嘉善县', '海盐县', '海宁市', '平湖市', '桐乡市'],
    '湖州市': ['吴兴区', '南浔区', '德清县', '长兴县', '安吉县'],
    '绍兴市': ['越城区', '柯桥区', '上虞区', '新昌县', '诸暨市', '嵊州市'],
    '金华市': ['婺城区', '金东区', '武义县', '浦江县', '磐安县', '兰溪市', '义乌市', '东阳市', '永康市'],
    '衢州市': ['柯城区', '衢江区', '常山县', '开化县', '龙游县', '江山市'],
    '舟山市': ['定海区', '普陀区', '岱山县', '嵊泗县'],
    '台州市': ['椒江区', '黄岩区', '路桥区', '三门县', '天台县', '仙居县', '温岭市', '临海市', '玉环市'],
    '丽水市': ['莲都区', '青田县', '缙云县', '遂昌县', '松阳县', '云和县', '庆元县', '景宁畲族自治县', '龙泉市'],
  },
  '江苏省': {
    '南京市': ['玄武区', '秦淮区', '建邺区', '鼓楼区', '浦口区', '栖霞区', '雨花台区', '江宁区', '六合区', '溧水区', '高淳区'],
    '无锡市': ['锡山区', '惠山区', '滨湖区', '梁溪区', '新吴区', '江阴市', '宜兴市'],
    '徐州市': ['鼓楼区', '云龙区', '贾汪区', '泉山区', '铜山区', '丰县', '沛县', '睢宁县', '新沂市', '邳州市'],
    '常州市': ['天宁区', '钟楼区', '新北区', '武进区', '金坛区', '溧阳市'],
    '苏州市': ['虎丘区', '吴中区', '相城区', '姑苏区', '吴江区', '常熟市', '张家港市', '昆山市', '太仓市'],
    '南通市': ['崇川区', '通州区', '海门区', '如东县', '启东市', '如皋市', '海安市'],
    '连云港市': ['连云区', '海州区', '赣榆区', '东海县', '灌云县', '灌南县'],
    '淮安市': ['淮安区', '淮阴区', '清江浦区', '洪泽区', '涟水县', '盱眙县', '金湖县'],
    '盐城市': ['亭湖区', '盐都区', '大丰区', '响水县', '滨海县', '阜宁县', '射阳县', '建湖县', '东台市'],
    '扬州市': ['广陵区', '邗江区', '江都区', '宝应县', '仪征市', '高邮市'],
    '镇江市': ['京口区', '润州区', '丹徒区', '丹阳市', '扬中市', '句容市'],
    '泰州市': ['海陵区', '高港区', '姜堰区', '兴化市', '靖江市', '泰兴市'],
    '宿迁市': ['宿城区', '宿豫区', '沭阳县', '泗阳县', '泗洪县'],
  },
}

// 省份列表
const provinces = computed(() => Object.keys(regionData))

// 城市列表
const cities = computed(() => {
  if (props.modelValue.province && regionData[props.modelValue.province]) {
    return Object.keys(regionData[props.modelValue.province])
  }
  return []
})

// 区县列表
const districts = computed(() => {
  if (props.modelValue.province && props.modelValue.city && regionData[props.modelValue.province]?.[props.modelValue.city]) {
    return regionData[props.modelValue.province][props.modelValue.city]
  }
  return []
})

// 处理省份变化
const handleProvinceChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', {
    province: target.value,
    city: '',
    district: '',
  })
}

// 处理城市变化
const handleCityChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', {
    ...props.modelValue,
    city: target.value,
    district: '',
  })
}

// 处理区县变化
const handleDistrictChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', {
    ...props.modelValue,
    district: target.value,
  })
}
</script>
